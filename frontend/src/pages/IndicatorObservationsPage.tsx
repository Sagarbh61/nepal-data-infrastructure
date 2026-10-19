
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";

import {
  fetchIndicator,
  fetchObservations,
  type Indicator,
  type IndicatorObservation,
} from "../services/api";

import "./IndicatorObservationsPage.css";

function IndicatorObservationsPage() {
  const { code } = useParams<{ code: string }>();

  const [indicator, setIndicator] = useState<Indicator | null>(null);
  const [observations, setObservations] = useState<
    IndicatorObservation[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    if (!code) {
      return;
    }

    const indicatorCode = code;
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [indicatorData, observationsData] = await Promise.all([
          fetchIndicator(indicatorCode),
          fetchObservations(indicatorCode),
        ]);

        if (cancelled) {
          return;
        }

        const sortedObservations = [...observationsData.results].sort(
          (a, b) => b.year - a.year,
        );

        setIndicator(indicatorData);
        setObservations(sortedObservations);
      } catch (err) {
        if (cancelled) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "An unexpected error occurred.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [code]);


  if (!code) {
    return (
      <main className="indicator-observations-page observations-page-content">
        <p className="observations-page-error" role="alert">
          No indicator code was provided.
        </p>

        <Link
          to="/explore"
          className="observations-page-back-link"
        >
          ← Back to Explore Data
        </Link>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="indicator-observations-page">
        <p className="observations-page-empty">
          Loading observations...
        </p>
      </main>
    );
  }

  if (error || !indicator) {
    return (
      <main className="indicator-observations-page observations-page-content">
        <p className="observations-page-error" role="alert">
          {error || "Indicator not found."}
        </p>

        <Link
          to="/explore"
          className="observations-page-back-link"
        >
          ← Back to Explore Data
        </Link>
      </main>
    );
  }

  const missingCount = observations.filter(
    (observation) =>
      observation.value === null ||
      observation.value.trim() === "",
  ).length;

  const availableCount = observations.length - missingCount;

  return (
    <main className="indicator-observations-page">
      <header className="observations-page-header">
        <Link
          to={`/indicators/${encodeURIComponent(indicator.code)}`}
          className="observations-page-back-link"
        >
          ← Back to indicator
        </Link>

        <h1>{indicator.name}</h1>

        <p>Complete historical observations for Nepal.</p>

        <span className="observations-page-code">
          {indicator.code}
        </span>
      </header>

      <section className="observations-page-content">
        <section>
          <div className="observations-page-section-heading">
            <h2>All observations</h2>

            <p>
              Historical values recorded for Nepal, ordered from newest
              to oldest.
            </p>

            <p className="observations-page-count">
              {observations.length} observations
            </p>
          </div>

          <div className="observations-page-summary">
            <div className="observations-page-summary-item">
              <p className="observations-page-summary-label">
                Total observations
              </p>

              <p className="observations-page-summary-value">
                {observations.length}
              </p>
            </div>

            <div className="observations-page-summary-item">
              <p className="observations-page-summary-label">
                Available values
              </p>

              <p className="observations-page-summary-value">
                {availableCount}
              </p>
            </div>

            <div className="observations-page-summary-item">
              <p className="observations-page-summary-label">
                Missing values
              </p>

              <p className="observations-page-summary-value">
                {missingCount}
              </p>
            </div>
          </div>

          {observations.length === 0 ? (
            <p className="observations-page-empty">
              No observations are available for this indicator.
            </p>
          ) : (
            <div className="observations-page-table-wrapper">
              <table className="observations-page-table">
                <thead>
                  <tr>
                    <th scope="col">Year</th>
                    <th scope="col">Value</th>
                  </tr>
                </thead>

                <tbody>
                  {observations.map((observation) => {
                    const rawValue = observation.value;

                    const parsedValue =
                      rawValue === null || rawValue.trim() === ""
                        ? null
                        : Number(rawValue);

                    const validValue =
                      parsedValue !== null &&
                      Number.isFinite(parsedValue);

                    return (
                      <tr
                        key={`${observation.country_code}-${observation.year}`}
                      >
                        <td>{observation.year}</td>

                        <td>
                          {!validValue
                            ? "Not available"
                            : parsedValue.toLocaleString("en-US", {
                                maximumSignificantDigits: 10,
                              })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default IndicatorObservationsPage;
