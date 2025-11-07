import logging
from typing import Optional
from enum import Enum

from openai import OpenAI

from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class RewriteStrategy(Enum):
    """Available query rewriting strategies."""

    EXPANSION = "expansion"  # Generate 3-4 variations of the query
    SIMPLIFICATION = "simplification"  # Remove noise, keep main concepts
    REFORMULATION = "reformulation"  # Rephrase for better matching
    COMBINED = "combined"  # Use all strategies and combine results


class QueryRewriter:
    """Service for rewriting and expanding queries to improve retrieval."""

    def __init__(self, client: Optional[OpenAI] = None):
        """Initialize the query rewriter with an OpenAI client."""
        if client is None:
            settings = get_settings()
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = client

    def expand_query(self, query: str, num_variations: int = 3) -> list[str]:
        if not query or len(query.strip()) < 3:
            return [query]

        prompt = f"""Você é um especialista em reformular perguntas sobre Vestibular Unicamp.

Gere {num_variations} variações diferentes da pergunta abaixo, cada uma com uma abordagem diferente:
1. Use sinônimos e termos alternativos
2. Reformule com estrutura gramatical diferente
3. Expanda com contexto adicional relevante

Pergunta original: "{query}"

Retorne APENAS as {num_variations} variações, uma por linha, sem numeração ou explicação."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em reformulação de perguntas. Retorne apenas as variações solicitadas, uma por linha.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content or ""
            variations = [line.strip() for line in content.split("\n") if line.strip()]

            # Ensure we include the original query
            queries = [query]
            queries.extend(variations[:num_variations])

            logger.debug(f"Query expansion: {len(queries)} queries generated")
            return queries

        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            return [query]

    def simplify_query(self, query: str) -> str:
        if not query or len(query.strip()) < 3:
            return query

        prompt = f"""Você é um especialista em simplificação de textos para buscas.

Simplifique a pergunta abaixo removendo palavras desnecessárias e mantendo apenas os conceitos principais:
- Remova palavras decorativas (muito, bastante, realmente, etc)
- Mantenha nomes, datas, números e termos técnicos
- Mantenha verbos e nouns essenciais
- Mantenha a intenção da pergunta

Pergunta original: "{query}"

Retorne APENAS a versão simplificada, sem explicação."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você simplifica perguntas mantendo apenas conceitos essenciais. Retorne apenas a versão simplificada.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            simplified = response.choices[0].message.content or query
            simplified = simplified.strip().strip('"')

            logger.debug(f"Query simplified: '{query}' -> '{simplified}'")
            return simplified

        except Exception as e:
            logger.error(f"Error simplifying query: {e}")
            return query

    def reformulate_query(self, query: str) -> str:
        """
        Reformulate the query to better match document language and terminology.

        This is particularly useful for bridging the gap between casual user language
        and technical documentation language.

        Args:
            query: The original user query

        Returns:
            Reformulated version of the query
        """
        if not query or len(query.strip()) < 3:
            return query

        prompt = f"""Você é um especialista em dados sobre vestibulares e da Unicamp.

Reformule a pergunta abaixo usando linguagem técnica adequada ao contexto de vestibular Unicamp:
- Use terminologia apropriada do domínio
- Seja mais específico se possível
- Mantenha a intenção original da pergunta
- Aumente a probabilidade de matching com documentos técnicos

Pergunta original: "{query}"

Retorne APENAS a versão reformulada, sem explicação."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você reformula perguntas usando linguagem técnica de vestibulares. Retorne apenas a versão reformulada.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=200,
            )

            reformulated = response.choices[0].message.content or query
            reformulated = reformulated.strip().strip('"')

            logger.debug(f"Query reformulated: '{query}' -> '{reformulated}'")
            return reformulated

        except Exception as e:
            logger.error(f"Error reformulating query: {e}")
            return query

    def rewrite(
        self, query: str, strategy: RewriteStrategy = RewriteStrategy.COMBINED
    ) -> list[str]:
        """
        Apply the specified rewriting strategy to generate better search queries.

        Args:
            query: The original user query
            strategy: The rewriting strategy to apply

        Returns:
            List of queries to use for retrieval (original + variations)
        """
        if not query or len(query.strip()) < 3:
            return [query]

        queries = [query]  # Always include original

        try:
            if strategy == RewriteStrategy.EXPANSION:
                queries.extend(self.expand_query(query, num_variations=3))

            elif strategy == RewriteStrategy.SIMPLIFICATION:
                simplified = self.simplify_query(query)
                if simplified != query:
                    queries.append(simplified)

            elif strategy == RewriteStrategy.REFORMULATION:
                reformulated = self.reformulate_query(query)
                if reformulated != query:
                    queries.append(reformulated)

            elif strategy == RewriteStrategy.COMBINED:
                # Apply all strategies
                queries.extend(self.expand_query(query, num_variations=2))

                simplified = self.simplify_query(query)
                if simplified != query:
                    queries.append(simplified)

                reformulated = self.reformulate_query(query)
                if reformulated != query:
                    queries.append(reformulated)

            # Remove duplicates while preserving order
            seen = set()
            unique_queries = []
            for q in queries:
                q_lower = q.lower().strip()
                if q_lower and q_lower not in seen:
                    seen.add(q_lower)
                    unique_queries.append(q)

            logger.info(
                f"Query rewriting ({strategy.value}): {len(unique_queries)} queries for retrieval"
            )
            return unique_queries

        except Exception as e:
            logger.error(f"Error in query rewriting: {e}")
            return [query]


# Singleton instance for reuse across the application
_rewriter_instance: Optional[QueryRewriter] = None


def get_query_rewriter() -> QueryRewriter:
    """Get or create the query rewriter singleton instance."""
    global _rewriter_instance
    if _rewriter_instance is None:
        _rewriter_instance = QueryRewriter()
    return _rewriter_instance
