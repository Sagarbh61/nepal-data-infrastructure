import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  fetchIndicator,
  fetchObservations,
  type Indicator,
  type IndicatorObservation,
} from "../services/api";

import "./IndicatorDetailPage.css";

function IndicatorDetailPage() {
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
          setError("Could not load this indicator. Please try again.");
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

  const chronologicalObservations = [...observations].sort(
    (a, b) => a.year - b.year,
  );

  // Convert stored values into numbers while preserving missing values.
  const chartData = chronologicalObservations.map((observation) => {
    const rawValue = observation.value;
    const parsedValue =
      rawValue === null || rawValue.trim() === ""
        ? null
        : Number(rawValue);

    return {
      year: observation.year,
      value:
        parsedValue !== null && Number.isFinite(parsedValue)
          ? parsedValue
          : null,
    };
  });

  // Keep only observations containing valid numerical values.
  const validObservations = chartData.filter(
    (observation): observation is {
      year: number;
      value: number;
    } => observation.value !== null,
  );

  const firstValidObservation = validObservations[0] ?? null;

  const latestValidObservation =
    validObservations[validObservations.length - 1] ?? null;

  // Raw numerical difference, not necessarily a percentage change.
  const numericalChange =
    firstValidObservation && latestValidObservation
      ? latestValidObservation.value - firstValidObservation.value
      : null;

  const missingValueCount =
    chartData.length - validObservations.length;

  const recentObservations = [...chronologicalObservations]
    .reverse()
    .slice(0, 5);

  const formatValue = (value: number) =>
    value.toLocaleString(undefined, {
      maximumSignificantDigits: 10,
    });


  const changeClass =
    numericalChange === null
      ? ""
      : numericalChange > 0
        ? "change-increase"
        : numericalChange < 0
          ? "change-decrease"
          : "change-neutral";

  const changeDisplay =
    numericalChange === null
      ? "Not available"
      : numericalChange > 0
        ? `↑ ${formatValue(numericalChange)}`
        : numericalChange < 0
          ? `↓ ${formatValue(Math.abs(numericalChange))}`
          : "— 0";

  if (loading) {
    return (
      <main className="indicator-detail-page">
        <p className="detail-status">Loading indicator...</p>
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
        <p className="explore-eyebrow">INDICATOR DETAILS</p>
        <h1>{indicator.name}</h1>
        <p className="detail-source">{indicator.source}</p>
        <span className="detail-code">{indicator.code}</span>
      </section>

      <section className="detail-content">
        <Link className="detail-back-link" to="/explore">
          ← Back to Explore Data
        </Link>

        <section className="analysis-summary">
          <div className="observations-heading">
            <h2>Data summary</h2>
            <p>
              Summary statistics calculated from the available observations.
            </p>
          </div>

          {validObservations.length === 0 ? (
            <p className="detail-status">
              No valid numerical observations are available for analysis.
            </p>
          ) : (
            <div className="summary-grid">
              <div className="summary-item">
                <p className="summary-label">Latest value</p>
                <p className="summary-value">
                  {formatValue(latestValidObservation!.value)}
                </p>
                <p className="summary-detail">
                  Year {latestValidObservation!.year}
                </p>
              </div>

              <div className="summary-item">
                <p className="summary-label">First available value</p>
                <p className="summary-value">
                  {formatValue(firstValidObservation!.value)}
                </p>
                <p className="summary-detail">
                  Year {firstValidObservation!.year}
                </p>
              </div>

              <div className="summary-item">
                <p className="summary-label">Numerical change</p>
                <p className={`summary-value ${changeClass}`}>
                  {changeDisplay}
                </p>
                <p className="summary-detail">
                  {numericalChange === null
                    ? "Insufficient observations"
                    : `${firstValidObservation!.year}–${latestValidObservation!.year}`}
                </p>
              </div>

              <div className="summary-item">
                <p className="summary-label">Missing values</p>
                <p className="summary-value">{missingValueCount}</p>
                <p className="summary-detail">
                  Of {chartData.length} recorded observations
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="chart-section">
          <div className="observations-heading">
            <h2>Historical trend</h2>
            <p>Annual observations reported for Nepal.</p>
          </div>

          {chartData.length === 0 ? (
            <p className="detail-status">
              No observations are available for this indicator.
            </p>
          ) : validObservations.length === 0 ? (
            <p className="detail-status">
              Observations exist, but none contains a valid numerical value
              to plot.
            </p>
          ) : (
            <div className="indicator-chart">
              <ResponsiveContainer width="100%" height={340}>
                <LineChart
                  data={chartData}
                  margin={{ top: 12, right: 20, left: 8, bottom: 8 }}
                >
                  <CartesianGrid
                    stroke="#e5e8e5"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="year"
                    type="number"
                    domain={["dataMin", "dataMax"]}
                    tick={{ fill: "#656b66", fontSize: 12 }}
                    tickLine={false}
                    axisLine={{ stroke: "#d7ddd8" }}
                    minTickGap={35}
                  />

                  <YAxis
                    tick={{ fill: "#656b66", fontSize: 12 }}
                    tickLine={false}
                    axisLine={false}
                    width={65}
                  />

                  <Tooltip
                    formatter={(value) =>
                      value == null
                        ? ["No data", "Value"]
                        : [
                            Number(value).toLocaleString(undefined, {
                              maximumSignificantDigits: 10,
                            }),
                            "Value",
                          ]
                    }
                    labelFormatter={(year) => `Year: ${year}`}
                  />

                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#29513d"
                    strokeWidth={2}
                    dot={false}
                    connectNulls={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="preview-section">
          <div className="preview-heading">
            <div className="observations-heading">
              <h2>Recent observations</h2>
              <p>Latest years in the dataset.</p>
            </div>

            <Link
              className="full-table-link"
              to={`/indicators/${encodeURIComponent(indicator.code)}/table`}
            >
              View full table →
            </Link>
          </div>

          {recentObservations.length === 0 ? (
            <p className="detail-status">
              No observations are available.
            </p>
          ) : (
            <div className="observation-table-wrapper">
              <table className="observation-table">
                <thead>
                  <tr>
                    <th scope="col">Year</th>
                    <th scope="col">Value</th>
                  </tr>
                </thead>

                <tbody>
                  {recentObservations.map((observation) => {
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
                            ? "No data"
                            : formatValue(parsedValue)}
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

export default IndicatorDetailPage;
