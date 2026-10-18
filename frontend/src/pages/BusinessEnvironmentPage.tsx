
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  fetchBusinessObstacles,
  fetchWBESMetadata,
  type BusinessObstacle,
  type WBESMetadata,
} from "../services/api";

import "./BusinessEnvironmentPage.css";

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function cleanObstacleLabel(label: string): string {
  return label.replace(/^How Much of An Obstacle:\s*/i, "");
}

function BusinessEnvironmentPage() {
  const [metadata, setMetadata] = useState<WBESMetadata | null>(null);
  const [obstacles, setObstacles] = useState<BusinessObstacle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const [metadataResult, obstacleResult] = await Promise.all([
          fetchWBESMetadata(),
          fetchBusinessObstacles(),
        ]);

        if (!cancelled) {
          setMetadata(metadataResult);
          setObstacles(
            [...obstacleResult.results].sort(
              (a, b) => b.weighted_share - a.weighted_share,
            ),
          );
        }
      } catch {
        if (!cancelled) {
          setError(
            "Could not load business-environment data. Check that the Django API is running.",
          );
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
  }, []);

  const weightingDifferences = [...obstacles]
    .map((obstacle) => ({
      ...obstacle,
      weighting_gap:
        obstacle.weighted_share - obstacle.unweighted_share,
    }))
    .sort(
      (a, b) =>
        Math.abs(b.weighting_gap) - Math.abs(a.weighting_gap),
    );

  const maxWeightingGap = Math.max(
    0.01,
    ...weightingDifferences.map((item) =>
      Math.abs(item.weighting_gap),
    ),
  );

  return (
    <main className="business-environment-page">
      <header className="business-environment-header">
        <p className="business-environment-eyebrow">
          WORLD BANK ENTERPRISE SURVEY · NEPAL 2023
        </p>

        <h1>Nepal's business environment</h1>

        <p>
          Explore the obstacles surveyed formal-sector establishments
          reported facing in their business operations.
        </p>
      </header>

      {loading && <p role="status">Loading survey data...</p>}

      {error && (
        <section className="business-environment-error" role="alert">
          <p>{error}</p>
        </section>
      )}

      {!loading && !error && metadata && (
        <>
          <section className="business-environment-overview">
            <article className="business-environment-info-card">
              <span>Survey period</span>
              <strong>{metadata.survey_period}</strong>
            </article>

            <article className="business-environment-info-card">
              <span>Establishments surveyed</span>
              <strong>
                {obstacles[0]?.total_records.toLocaleString() ?? "—"}
              </strong>
            </article>

            <article className="business-environment-info-card">
              <span>Indicators</span>
              <strong>{obstacles.length}</strong>
            </article>
          </section>

          <section className="business-environment-methodology">
            <h2>What do these percentages measure?</h2>

            <p>{metadata.measure}</p>
            <p>{metadata.population_covered}</p>

            <p>
              The main results use the{" "}
              <strong>{metadata.weighting.primary_weight}</strong> sampling
              weight. A higher percentage means a larger weighted share of
              valid survey responses rated that obstacle as major or very severe.
            </p>
          </section>

          <section className="business-environment-results">
            <div className="business-environment-section-heading">
              <div>
                <h2>Reported business obstacles</h2>
                <p>
                  Ranked by weighted share of valid responses rating each
                  obstacle as major or very severe.
                </p>
              </div>
            </div>

            {obstacles.length > 0 && (
              <section
                className="business-environment-chart"
                aria-labelledby="business-environment-chart-title"
              >
                <h3 id="business-environment-chart-title">
                  Which obstacles stand out?
                </h3>

                <p>
                  Percentage of valid responses rating each obstacle as a
                  major or very severe constraint. Results use survey weights.
                </p>

                <div className="business-environment-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={obstacles}
                      layout="vertical"
                      margin={{
                        top: 8,
                        right: 24,
                        bottom: 8,
                        left: 8,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={false}
                      />

                      <XAxis
                        type="number"
                        domain={[0, 1]}
                        tickFormatter={(value) =>
                          `${(Number(value) * 100).toFixed(0)}%`
                        }
                        tick={{ fontSize: 12 }}
                      />

                      <YAxis
                        type="category"
                        dataKey="label"
                        width={220}
                        tickFormatter={cleanObstacleLabel}
                        tick={{ fontSize: 11 }}
                      />

                      <Tooltip
                        formatter={(value) => [
                          formatPercent(Number(value)),
                          "Weighted share",
                        ]}
                        labelFormatter={(label) =>
                          cleanObstacleLabel(String(label))
                        }
                      />

                      <Bar
                        dataKey="weighted_share"
                        name="Weighted share"
                        fill="#438566"
                        radius={[0, 4, 4, 0]}
                        barSize={18}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            )}

            {obstacles.length > 0 && (
              <section
                className="business-environment-chart"
                aria-labelledby="business-environment-comparison-title"
              >
                <h3 id="business-environment-comparison-title">
                  Weighted vs. unweighted results
                </h3>

                <p>
                  Compare the survey-weighted share with the percentage
                  calculated directly from valid responses. Differences can
                  reflect the survey's sampling design.
                </p>

                <div className="business-environment-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={obstacles}
                      layout="vertical"
                      margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={false}
                      />

                      <XAxis
                        type="number"
                        domain={[0, 1]}
                        tickFormatter={(value) =>
                          `${(Number(value) * 100).toFixed(0)}%`
                        }
                        tick={{ fontSize: 12 }}
                      />

                      <YAxis
                        type="category"
                        dataKey="label"
                        width={220}
                        tickFormatter={cleanObstacleLabel}
                        tick={{ fontSize: 11 }}
                      />

                      <Tooltip
                        formatter={(value, name) => [
                          formatPercent(Number(value)),
                          String(name),
                        ]}
                        labelFormatter={(label) =>
                          cleanObstacleLabel(String(label))
                        }
                      />

                      <Legend />

                      <Bar
                        dataKey="weighted_share"
                        name="Weighted"
                        fill="#438566"
                        radius={[0, 3, 3, 0]}
                        barSize={10}
                      />

                      <Bar
                        dataKey="unweighted_share"
                        name="Unweighted"
                        fill="#7398bd"
                        radius={[0, 3, 3, 0]}
                        barSize={10}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            )}

            {obstacles.length > 0 && (
              <section
                className="business-environment-chart"
                aria-labelledby="business-environment-coverage-title"
              >
                <h3 id="business-environment-coverage-title">
                  Response coverage by obstacle
                </h3>

                <p>
                  Each bar separates valid responses from excluded responses.
                  Counts show the available records for each survey question.
                </p>

                <div className="business-environment-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={obstacles}
                      layout="vertical"
                      margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={false}
                      />

                      <XAxis
                        type="number"
                        domain={[0, "dataMax"]}
                        tick={{ fontSize: 12 }}
                      />

                      <YAxis
                        type="category"
                        dataKey="label"
                        width={220}
                        tickFormatter={cleanObstacleLabel}
                        tick={{ fontSize: 11 }}
                      />

                      <Tooltip
                        formatter={(value, name) => [
                          Number(value).toLocaleString(),
                          String(name),
                        ]}
                        labelFormatter={(label) =>
                          cleanObstacleLabel(String(label))
                        }
                      />

                      <Legend />

                      <Bar
                        dataKey="valid_responses"
                        name="Valid responses"
                        stackId="responses"
                        fill="#438566"
                      />

                      <Bar
                        dataKey="excluded_responses"
                        name="Excluded responses"
                        stackId="responses"
                        fill="#d5a45c"
                        radius={[0, 3, 3, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            )}

            {obstacles.length > 0 && (
              <section
                className="business-environment-chart"
                aria-labelledby="business-environment-gap-title"
              >
                <h3 id="business-environment-gap-title">
                  How much do the estimates change with weighting?
                </h3>

                <p>
                  Difference in percentage points: weighted share minus
                  unweighted share. Positive values mean the weighted
                  estimate is higher; negative values mean it is lower.
                </p>

                <div className="business-environment-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={weightingDifferences}
                      layout="vertical"
                      margin={{ top: 8, right: 28, bottom: 8, left: 8 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={false}
                      />

                      <XAxis
                        type="number"
                        domain={[-maxWeightingGap, maxWeightingGap]}
                        tickFormatter={(value) =>
                          `${(Number(value) * 100).toFixed(1)} pp`
                        }
                        tick={{ fontSize: 11 }}
                      />

                      <YAxis
                        type="category"
                        dataKey="label"
                        width={220}
                        tickFormatter={cleanObstacleLabel}
                        tick={{ fontSize: 11 }}
                      />

                      <ReferenceLine x={0} stroke="#53636e" />

                      <Tooltip
                        formatter={(value) => [
                          `${(Number(value) * 100).toFixed(2)} percentage points`,
                          "Weighted minus unweighted",
                        ]}
                        labelFormatter={(label) =>
                          cleanObstacleLabel(String(label))
                        }
                      />

                      <Bar
                        dataKey="weighting_gap"
                        name="Difference"
                        fill="#7398bd"
                        radius={[3, 3, 3, 3]}
                        barSize={16}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            )}

            <div className="business-environment-table-wrap">
              <table className="business-environment-table">
                <thead>
                  <tr>
                    <th scope="col">Obstacle</th>
                    <th scope="col">Major or very severe</th>
                    <th scope="col">Valid responses</th>
                    <th scope="col">Excluded</th>
                  </tr>
                </thead>

                <tbody>
                  {obstacles.map((obstacle) => (
                    <tr key={obstacle.obstacle}>
                      <td>
                        <strong>
                          {cleanObstacleLabel(obstacle.label)}
                        </strong>

                        <span className="business-environment-code">
                          {obstacle.obstacle}
                        </span>
                      </td>

                      <td>
                        <div className="business-environment-share">
                          <strong>
                            {formatPercent(obstacle.weighted_share)}
                          </strong>

                          <div
                            className="business-environment-bar-track"
                            role="img"
                            aria-label={`${formatPercent(
                              obstacle.weighted_share,
                            )} weighted share`}
                          >
                            <div
                              className="business-environment-bar"
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    obstacle.weighted_share * 100,
                                  ),
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      </td>

                      <td>
                        {obstacle.valid_responses.toLocaleString()}
                      </td>

                      <td>
                        {obstacle.excluded_responses.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="business-environment-limitations">
            <h2>How to interpret the results</h2>

            <ul>
              {metadata.limitations.map((limitation) => (
                <li key={limitation}>{limitation}</li>
              ))}
            </ul>
          </section>
        </>
      )}
    </main>
  );
}

export default BusinessEnvironmentPage;


