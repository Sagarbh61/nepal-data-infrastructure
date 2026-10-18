
import { useEffect, useMemo, useState } from "react";
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

import { calculateAnnualChanges } from "../utils/annualChanges";
import "./IndicatorDetailPage.css";

function IndicatorDetailPage() {
  const { code } = useParams();

  const [indicator, setIndicator] = useState<Indicator | null>(null);
  const [observations, setObservations] = useState<
    IndicatorObservation[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [startYear, setStartYear] = useState<number | "">("");
  const [endYear, setEndYear] = useState<number | "">("");

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
          setStartYear("");
          setEndYear("");
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

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [code]);

  const chronologicalObservations = useMemo(
    () => [...observations].sort((a, b) => a.year - b.year),
    [observations],
  );

  const chartData = useMemo(
    () =>
      chronologicalObservations.map((observation) => {
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
      }),
    [chronologicalObservations],
  );

  const validObservations = useMemo(
    () =>
      chartData.filter(
        (observation): observation is {
          year: number;
          value: number;
        } => observation.value !== null,
      ),
    [chartData],
  );

  const firstValidObservation = validObservations[0] ?? null;

  const latestValidObservation =
    validObservations[validObservations.length - 1] ?? null;

  const numericalChange =
    firstValidObservation !== null && latestValidObservation !== null
      ? latestValidObservation.value - firstValidObservation.value
      : null;

  const missingValueCount =
    chartData.length - validObservations.length;

  const annualChangeData = useMemo(
    () =>
      calculateAnnualChanges(
        chronologicalObservations.map((observation) => ({
          year: observation.year,
          value: observation.value,
        })),
      ),
    [chronologicalObservations],
  );

  const recentObservations = useMemo(
    () => [...chronologicalObservations].reverse().slice(0, 5),
    [chronologicalObservations],
  );

  const years = useMemo(
    () =>
      [...new Set(chartData.map((observation) => observation.year))].sort(
        (a, b) => a - b,
      ),
    [chartData],
  );

  const availableYears = validObservations.map(
    (observation) => observation.year,
  );

  const effectiveStartYear: number | null =
    startYear === "" ? (availableYears[0] ?? null) : startYear;

  const effectiveEndYear: number | null =
    endYear === ""
      ? (availableYears[availableYears.length - 1] ?? null)
      : endYear;

  const selectedStartObservation =
    effectiveStartYear === null
      ? null
      : validObservations.find(
          (observation) => observation.year === effectiveStartYear,
        ) ?? null;

  const selectedEndObservation =
    effectiveEndYear === null
      ? null
      : validObservations.find(
          (observation) => observation.year === effectiveEndYear,
        ) ?? null;

  const periodAbsoluteChange =
    selectedStartObservation !== null &&
    selectedEndObservation !== null &&
    effectiveStartYear !== null &&
    effectiveEndYear !== null &&
    effectiveEndYear > effectiveStartYear
      ? selectedEndObservation.value - selectedStartObservation.value
      : null;

  const periodIsValid = periodAbsoluteChange !== null;

  const periodPercentageChange =
    periodIsValid &&
    selectedStartObservation !== null &&
    selectedStartObservation.value !== 0
      ? (periodAbsoluteChange / Math.abs(selectedStartObservation.value)) *
        100
      : null;

  const periodChartData = chartData.filter(
    (observation) =>
      effectiveStartYear !== null &&
      effectiveEndYear !== null &&
      observation.year >= effectiveStartYear &&
      observation.year <= effectiveEndYear,
  );

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
        <p className="detail-error" role="alert">
          {error || "Indicator not found."}
        </p>
        <Link to="/explore" className="detail-back-link">
          ← Back to Explore Data
        </Link>
      </main>
    );
  }

  return (
    <main className="indicator-detail-page">
      <div className="detail-top-navigation">
        <Link className="detail-back-link" to="/explore">
          ← Back to Explore Data
        </Link>
      </div>

      <div className="indicator-detail-layout">
        <aside
          className="detail-sidebar"
          aria-label="Indicator page navigation"
        >
          <p className="detail-sidebar-title">TABLE OF CONTENTS</p>

          <nav className="detail-sidebar-nav">
            <a href="#indicator-details">Details</a>
            <a href="#data-summary">Data summary</a>
            <a href="#historical-trend">Historical trend</a>
            <a href="#changes-over-time">Changes over time</a>

            <Link
              to={`/indicators/${encodeURIComponent(indicator.code)}/observations`}
            >
              Historical observations
              <span className="sidebar-external-icon" aria-hidden="true">
                ↗
              </span>
            </Link>

            <a href="#source-methodology">Source &amp; methodology</a>
          </nav>
        </aside>

        <div className="detail-main-column">
          <header className="detail-header" id="indicator-details">
            <p className="detail-eyebrow">INDICATOR DETAILS</p>
            <h1>{indicator.name}</h1>
            <p className="detail-source">{indicator.source}</p>
            <span className="detail-code">{indicator.code}</span>
          </header>

          <div className="detail-content">
            <section className="analysis-summary" id="data-summary">
              <div className="observations-heading">
                <h2>Data summary</h2>
                <p>
                  Summary statistics calculated from the available
                  observations.
                </p>
              </div>

              {validObservations.length === 0 ? (
                <p className="detail-status">
                  No valid numerical observations available for analysis.
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

            <section className="period-section" id="period-comparison">
              <div className="observations-heading">
                <h2>Period comparison</h2>
                <p>
                  Compare the recorded values at two selected years.
                </p>
              </div>

              {validObservations.length < 2 ? (
                <p className="detail-status">
                  At least two valid observations are needed for a period
                  comparison.
                </p>
              ) : (
                <>
                  <div className="period-controls">
                    <label>
                      Start year
                      <select
                        value={effectiveStartYear ?? ""}
                        onChange={(event) => {
                          const selectedYear = Number(event.target.value);
                          setStartYear(selectedYear);
                          setEndYear("");
                        }}
                      >
                        {years
                          .filter((year) => availableYears.includes(year))
                          .filter(
                            (year) =>
                              effectiveEndYear === null ||
                              year < effectiveEndYear,
                          )
                          .map((year) => (
                            <option key={year} value={year}>
                              {year}
                            </option>
                          ))}
                      </select>
                    </label>

                    <label>
                      End year
                      <select
                        value={effectiveEndYear ?? ""}
                        onChange={(event) =>
                          setEndYear(Number(event.target.value))
                        }
                      >
                        {years
                          .filter((year) => availableYears.includes(year))
                          .filter(
                            (year) =>
                              effectiveStartYear === null ||
                              year > effectiveStartYear,
                          )
                          .map((year) => (
                            <option key={year} value={year}>
                              {year}
                            </option>
                          ))}
                      </select>
                    </label>
                  </div>

                  {!periodIsValid ||
                  selectedStartObservation === null ||
                  selectedEndObservation === null ? (
                    <p className="detail-status">
                      Select two different years with valid observations.
                    </p>
                  ) : (
                    <>
                      <div className="period-summary-grid">
                        <div className="summary-item">
                          <p className="summary-label">Starting value</p>
                          <p className="summary-value">
                            {formatValue(selectedStartObservation.value)}
                          </p>
                          <p className="summary-detail">
                            Year {selectedStartObservation.year}
                          </p>
                        </div>

                        <div className="summary-item">
                          <p className="summary-label">Ending value</p>
                          <p className="summary-value">
                            {formatValue(selectedEndObservation.value)}
                          </p>
                          <p className="summary-detail">
                            Year {selectedEndObservation.year}
                          </p>
                        </div>

                        <div className="summary-item">
                          <p className="summary-label">Absolute change</p>
                          <p
                            className={`summary-value ${
                              periodAbsoluteChange > 0
                                ? "change-increase"
                                : periodAbsoluteChange < 0
                                  ? "change-decrease"
                                  : "change-neutral"
                            }`}
                          >
                            {periodAbsoluteChange > 0 ? "+" : ""}
                            {formatValue(periodAbsoluteChange)}
                          </p>
                          <p className="summary-detail">
                            Ending minus starting value
                          </p>
                        </div>

                        <div className="summary-item">
                          <p className="summary-label">Percentage change</p>
                          <p className="summary-value">
                            {periodPercentageChange === null
                              ? "Unavailable"
                              : `${periodPercentageChange > 0 ? "+" : ""}${formatValue(periodPercentageChange)}%`}
                          </p>
                          <p className="summary-detail">
                            {periodPercentageChange === null
                              ? "Starting value is zero"
                              : "Relative to starting value"}
                          </p>
                        </div>
                      </div>

                      <div className="period-chart">
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={periodChartData}>
                            <CartesianGrid
                              stroke="#e5e8e5"
                              vertical={false}
                            />
                            <XAxis
                              dataKey="year"
                              type="number"
                              domain={[
                                effectiveStartYear ?? "dataMin",
                                effectiveEndYear ?? "dataMax",
                              ]}
                              tick={{ fill: "#656b66", fontSize: 12 }}
                              tickLine={false}
                              axisLine={{ stroke: "#d7ddd8" }}
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
                                  : [formatValue(Number(value)), "Value"]
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
                    </>
                  )}
                </>
              )}
            </section>

            <section className="chart-section" id="historical-trend">
              <div className="observations-heading">
                <h2>Historical trend</h2>
                <p>All annual observations reported for Nepal.</p>
              </div>

              {chartData.length === 0 ? (
                <p className="detail-status">
                  No observations available for this indicator.
                </p>
              ) : validObservations.length === 0 ? (
                <p className="detail-status">
                  Observations exist, but none contains a valid numerical
                  value to plot.
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
                            : [formatValue(Number(value)), "Value"]
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

            <section className="preview-section" id="changes-over-time">
              <div className="preview-heading">
                <div className="observations-heading">
                  <h2>Annual changes</h2>
                  <p>
                    Year-over-year changes for consecutive years with valid
                    data.
                  </p>
                </div>

                <Link
                  className="full-table-link"
                  to={`/indicators/${encodeURIComponent(indicator.code)}/changes`}
                >
                  View all changes →
                </Link>
              </div>

              {annualChangeData.length === 0 ? (
                <p className="detail-status">
                  No observations available.
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
                      {annualChangeData
                        .slice(-5)
                        .reverse()
                        .map((observation) => (
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

            <section className="preview-section" id="recent-observations">
              <div className="preview-heading">
                <div className="observations-heading">
                  <h2>Recent observations</h2>
                  <p>Latest years in the dataset.</p>
                </div>

                <Link
                  className="full-table-link"
                  to={`/indicators/${encodeURIComponent(indicator.code)}/observations`}
                >
                  View full table →
                </Link>
              </div>

              {recentObservations.length === 0 ? (
                <p className="detail-status">
                  No observations available.
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

            <section
              className="methodology-section"
              id="source-methodology"
            >
              <div className="observations-heading">
                <h2>Source &amp; methodology</h2>
                <p>
                  Source details, indicator definitions, and documented
                  limitations.
                </p>
              </div>

              <div className="methodology-item">
                <h3>Data source</h3>
                <p>{indicator.source}</p>
              </div>

              <div className="methodology-item">
                <h3>Definition</h3>
                <p>
                  A verified definition has not yet been added for this
                  indicator.
                </p>
              </div>

              <div className="methodology-item">
                <h3>Limitations</h3>
                <p>
                  Indicator-specific limitations have not yet been documented.
                  Missing values are counted separately from valid numerical
                  observations.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}

export default IndicatorDetailPage;
