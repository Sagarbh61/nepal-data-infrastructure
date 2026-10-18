
import { useEffect, useState } from "react";
import { Link } from "react-router";
import {
  fetchIndicators,
  type Indicator,
} from "../services/api";
import "./ExploreDataPage.css";

function ExplorerDataPage() {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [showIndicators, setShowIndicators] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const pageSize = 20;
  const totalPages = Math.ceil(totalCount / pageSize);

  useEffect(() => {
    if (!showIndicators) return;

    let cancelled = false;

    async function loadIndicators() {
      setLoading(true);
      setError("");

      try {
        const data = await fetchIndicators(page);

        if (!cancelled) {
          setIndicators(data.results);
          setTotalCount(data.count);
        }
      } catch {
        if (!cancelled) {
          setError(
            "Could not load indicators. Check that the Django API is running.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadIndicators();

    return () => {
      cancelled = true;
    };
  }, [page, showIndicators]);

  const filteredIndicators = indicators.filter((indicator) => {
    const query = search.trim().toLowerCase();

    return (
      indicator.name.toLowerCase().includes(query) ||
      indicator.code.toLowerCase().includes(query) ||
      indicator.source.toLowerCase().includes(query)
    );
  });

  function openIndicatorCatalog() {
    setShowIndicators(true);
    setPage(1);
    setSearch("");
  }

  return (
    <main className="explore-page">
      <section className="explore-header">
        <h1>Explore Nepal's data</h1>
        <p>
          Discover datasets about Nepal's population, economy, and development.
          Explore geographic records and indicators from trusted sources.
        </p>
      </section>

      {!showIndicators ? (
        <section className="indicator-section">
          <div className="section-heading">
            <div>
              <h2>Browse datasets</h2>
              <p>
                Choose a collection to explore its data and available measures.
              </p>
            </div>
          </div>

          <div className="dataset-grid">
            <article className="dataset-card">
              <div className="dataset-card-top">
                <span className="dataset-category">POPULATION · CENSUS</span>
                <span className="dataset-year">2021</span>
              </div>

              <h3>National Population and Housing Census</h3>
              <p>
                Explore population totals, sex composition, households, and
                local governments across Nepal.
              </p>

              <div className="dataset-meta">
                <span>Geographic coverage: Nepal</span>
                <span>Level: Local government</span>
              </div>

              <Link className="dataset-link" to="/population">
                Explore population data <span aria-hidden="true">→</span>
              </Link>
            </article>

            <article className="dataset-card">
              <div className="dataset-card-top">
                <span className="dataset-category">ECONOMY · DEVELOPMENT</span>
                <span className="dataset-year">Time series</span>
              </div>

              <h3>World Development Indicators</h3>
              <p>
                Explore economic, social, health, education, and development
                measures over time.
              </p>

              <div className="dataset-meta">
                <span>Geographic coverage: Country-level</span>
                <span>Source: World Bank</span>
              </div>

              <button
                className="dataset-link"
                type="button"
                onClick={openIndicatorCatalog}
              >
                Browse indicators <span aria-hidden="true">→</span>
              </button>
            </article>
          </div>

          <div className="catalog-note">
            <h3>About this catalog</h3>
            <p>
              Each collection has its own exploration tools because datasets
              differ in geographic structure, time coverage, and available
              measurements.
            </p>
          </div>
        </section>
      ) : (
        <section className="indicator-section">
          <div className="section-heading">
            <div>
              <button
                className="catalog-back-link"
                type="button"
                onClick={() => setShowIndicators(false)}
              >
                ← All datasets
              </button>
              <h2>World Development Indicators</h2>
              <p>
                Browse indicators from the World Bank's development data
                collection.
              </p>
            </div>

            <span className="result-count">
              {totalCount.toLocaleString()} indicators
            </span>
          </div>

          <label className="search-label" htmlFor="indicator-search">
            Search indicators
          </label>

          <input
            id="indicator-search"
            className="indicator-search"
            type="search"
            placeholder="Search by name, code, or source..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          {loading && (
            <p className="status-message">Loading indicators...</p>
          )}

          {!loading && error && (
            <p className="status-message error-message">{error}</p>
          )}

          {!loading && !error && (
            <>
              <div className="indicator-list">
                {filteredIndicators.map((indicator) => (
                  <article className="indicator-card" key={indicator.code}>
                    <div>
                      <h3>
                        <Link
                          to={`/indicators/${encodeURIComponent(indicator.code)}`}
                        >
                          {indicator.name}
                        </Link>
                      </h3>
                      <p>{indicator.source}</p>
                    </div>

                    <span className="indicator-code">{indicator.code}</span>
                  </article>
                ))}
              </div>

              {filteredIndicators.length === 0 && (
                <p className="status-message">
                  No indicators match your search on this page.
                </p>
              )}

              <div className="pagination">
                <button
                  type="button"
                  disabled={page === 1}
                  onClick={() => setPage((current) => current - 1)}
                >
                  Previous
                </button>

                <span>
                  Page {page} of {totalPages || 1}
                </span>

                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </div>
            </>
          )}
        </section>
      )}
    </main>
  );
}

export default ExplorerDataPage;
