import logging
import sys
import io
from datetime import date
from pathlib import Path

_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace") if hasattr(sys.stdout, "buffer") else sys.stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(_stdout)],
)
logger = logging.getLogger(__name__)


def run_pipeline(
    db_path: Path = None,
    delay_between_queries: float = 2.5,
    dry_run: bool = False,
    use_trusted_filter: bool = True,
) -> dict:
    from dotenv import load_dotenv
    load_dotenv()

    from config.settings import DB_PATH, BANK_QUERIES, TRUSTED_DOMAINS
    from db.database import initialize_db, insert_article, get_connection, count_articles
    from scraper.fetcher import fetch_all_banks
    from scraper.classifier import classify_esg
    from scraper.dedup import compute_title_hash
    from scraper.ai_classifier import verify_and_classify, is_ai_available
    from scraper.models import ClassifiedArticle

    if db_path is None:
        db_path = DB_PATH

    summary = {"total_fetched": 0, "total_inserted": 0, "total_skipped": 0, "errors": []}

    ai_active = is_ai_available()
    logger.info(f"AI verification: {'ACTIVE (Azure OpenAI)' if ai_active else 'INACTIVE (keyword fallback)'}")

    logger.info("Initializing database...")
    initialize_db(db_path)

    logger.info("Starting fetch from Google News RSS...")
    trusted = TRUSTED_DOMAINS if use_trusted_filter else None
    raw_results = fetch_all_banks(BANK_QUERIES, delay_seconds=delay_between_queries, trusted_domains=trusted)

    current_year = date.today().year

    with get_connection(db_path) as conn:
        for banco_tag, articles in raw_results:
            for raw in articles:
                summary["total_fetched"] += 1
                # Descarta artigos de anos diferentes do ano corrente
                if raw["data"].year != current_year:
                    summary["total_skipped"] += 1
                    continue
                try:
                    keyword_tag = classify_esg(f"{raw.get('titulo', '')} {raw.get('resumo', '') or ''}")
                    title_hash = compute_title_hash(raw["titulo"], raw["data"])

                    if ai_active:
                        ai_result = verify_and_classify(
                            raw["titulo"], raw.get("resumo"), banco_tag, keyword_tag
                        )
                        if not ai_result.get("is_esg_related") or ai_result.get("is_fake_or_noise"):
                            summary["total_skipped"] += 1
                            logger.debug(f"[SKIP AI] {raw['titulo'][:60]}")
                            continue
                        final_tag = ai_result.get("esg_tag") or keyword_tag
                        ai_verified = True
                        ai_reasoning = ai_result.get("reasoning")
                        is_fake_flag = bool(ai_result.get("is_fake_or_noise", False))
                    else:
                        final_tag = keyword_tag
                        ai_verified = False
                        ai_reasoning = None
                        is_fake_flag = False

                    classified = ClassifiedArticle(
                        titulo=raw["titulo"],
                        link=raw["link"],
                        data=raw["data"],
                        resumo=raw.get("resumo"),
                        fonte=raw.get("fonte"),
                        banco_tag=banco_tag,
                        esg_tag=final_tag,
                        title_hash=title_hash,
                        ai_verified=ai_verified,
                        ai_reasoning=ai_reasoning,
                        is_fake_flag=is_fake_flag,
                    )

                    if dry_run:
                        logger.info(
                            f"[DRY RUN] {classified.banco_tag} | {classified.esg_tag} | "
                            f"{'AI' if ai_verified else 'KW'} | {classified.titulo[:60]}"
                        )
                        summary["total_inserted"] += 1
                    else:
                        inserted = insert_article(conn, classified)
                        if inserted:
                            summary["total_inserted"] += 1
                            logger.info(
                                f"[NEW] {classified.banco_tag} | {classified.esg_tag} | "
                                f"{'AI' if ai_verified else 'KW'} | {classified.titulo[:60]}"
                            )
                        else:
                            summary["total_skipped"] += 1
                except Exception as e:
                    summary["errors"].append(str(e))
                    logger.error(f"Failed to process article: {e}")

        if not dry_run:
            total = count_articles(conn)
            logger.info(f"Database now has {total} articles total.")

    logger.info(
        f"Pipeline complete: fetched={summary['total_fetched']}, "
        f"inserted={summary['total_inserted']}, "
        f"skipped={summary['total_skipped']}, "
        f"errors={len(summary['errors'])}"
    )
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ESG News Scraper Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and classify without writing to DB")
    parser.add_argument("--delay", type=float, default=2.5, help="Delay between RSS requests (seconds)")
    parser.add_argument("--no-filter", action="store_true", help="Disable trusted domain whitelist")
    args = parser.parse_args()

    run_pipeline(
        delay_between_queries=args.delay,
        dry_run=args.dry_run,
        use_trusted_filter=not args.no_filter,
    )
