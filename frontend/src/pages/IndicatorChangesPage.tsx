
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";

import {
  fetchIndicator,
  fetchObservations,
  type Indicator,
  type IndicatorObservation,
} from "../services/api";

import { calculateAnnualChanges } from "../utils/annualChanges";
import "./IndicatorDetailPage.css";

function IndicatorChangesPage() {
  const { code } = useParams();

  const [indicator, setIndicator] = useState<Indicator | null>(null);
  const [observations, setObservations] = useState<
    IndicatorObservation[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      if (!code) {
        setError("No indicator code was provided.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");

      try {
        const [indicatorData, observationData] = await Promise.all([
          fetchIndicator(code),
          fetchObservations(code),
        ]);

        if (!cancelled) {
          setIndicator(indicatorData);
          setObservations(observationData.results);
        }
      } catch {
        if (!cancelled) {
          setError("Could not load annual changes. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, [code]);

  const annualChanges = calculateAnnualChanges(
    observations.map((observation) => ({
      year: observation.year,
      value: observation.value,
    })),
  ).reverse();

  const formatValue = (value: number) =>
    value.toLocaleString(undefined, {
      maximumSignificantDigits: 10,
    });

  if (loading) {
    return (
      <main className="indicator-detail-page">
        <p className="detail-status">Loading annual changes...</p>
      </main>
    );
  }

  if (error || !indicator) {
    return (
      <main className="indicator-detail-page detail-content">
        <p className="detail-error">
          {error || "Indicator not found."}
        </p>
        <Link to="/explore">Back to Explore Data</Link>
      </main>
    );
  }

  return (
    <main className="indicator-detail-page">
      <section className="detail-header">
        <p className="explore-eyebrow">INDICATOR ANALYSIS</p>
        <h1>Annual changes</h1>
        <p className="detail-source">{indicator.name}</p>
        <span className="detail-code">{indicator.code}</span>
      </section>

      <section className="detail-content">
        <Link
          className="detail-back-link"
          to={`/indicators/${encodeURIComponent(indicator.code)}`}
        >
          ← Back to indicator details
        </Link>

        <section className="preview-section">
          <div className="observations-heading">
            <h2>Year-over-year changes</h2>
            <p>
              Changes are calculated only when valid observations exist
              for consecutive years. A dash means the change cannot be
              calculated reliably from the available data.
            </p>
          </div>

          {annualChanges.length === 0 ? (
            <p className="detail-status">
              No observations are available for this indicator.
            </p>
          ) : (
            <div className="observation-table-wrapper">
              <table className="observation-table">
                <thead>
                  <tr>
                    <th scope="col">Year</th>
                    <th scope="col">Value</th>
                    <th scope="col">Absolute change</th>
                    <th scope="col">Percentage change</th>
                  </tr>
                </thead>

                <tbody>
                  {annualChanges.map((observation) => (
                    <tr key={observation.year}>
                      <td>{observation.year}</td>
                      <td>
                        {observation.value === null
                          ? "No data"
                          : formatValue(observation.value)}
                      </td>
                      <td>
                        {observation.absoluteChange === null
                          ? "—"
                          : `${observation.absoluteChange > 0 ? "+" : ""}${formatValue(observation.absoluteChange)}`}
                      </td>
                      <td>
                        {observation.percentageChange === null
                          ? "—"
                          : `${observation.percentageChange > 0 ? "+" : ""}${formatValue(observation.percentageChange)}%`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default IndicatorChangesPage;
