
import { useEffect, useState } from "react";
import {
  fetchIndicators,
  type Indicator,
} from "../services/api";
import "./ExploreDataPage.css";
import { Link } from "react-router";

function ExploreDataPage() {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const pageSize = 20;
  const totalPages = Math.ceil(totalCount / pageSize);

  useEffect(() => {
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

    loadIndicators();

    return () => {
      cancelled = true;
    };
  }, [page]);

  const filteredIndicators = indicators.filter((indicator) => {
    const query = search.trim().toLowerCase();

    return (
      indicator.name.toLowerCase().includes(query) ||
      indicator.code.toLowerCase().includes(query) ||
      indicator.source.toLowerCase().includes(query)
    );
  });

  return (
    <main className="explore-page">
      <section className="explore-header">

        <h1>SAKSHARTHA DATA CATALOG</h1>
        <p>
          Discover Nepal's population, economic, and development data
          through structured datasets and indicators.
        </p>
      </section>

      <section className="indicator-section">
        <div className="section-heading">
          <div>
            <h2>Development indicators</h2>
            <p>
              Browse indicators from the World Development Indicators
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

        {loading && <p className="status-message">Loading indicators...</p>}

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
  <Link to={`/indicators/${encodeURIComponent(indicator.code)}`}>
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
    </main>
  );
}

export default ExploreDataPage;
