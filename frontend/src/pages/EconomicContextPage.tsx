
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";

import {
  fetchObservations,
  fetchWBESMetadata,
  fetchBusinessObstacles,
  type IndicatorObservation,
  type WBESMetadata,
  type BusinessObstacle,
} from "../services/api";

import "./EconomicContextPage.css";

const GDP_PER_CAPITA = "NY.GDP.PCAP.KD";
const GDP_PER_CAPITA_GROWTH = "NY.GDP.PCAP.KD.ZG";

interface ChartObservation {
  year: number;
  value: number | null;
}

function toChartData(
  observations: IndicatorObservation[],
): ChartObservation[] {
  return [...observations]
    .map((observation) => {
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
    })
    .sort((a, b) => a.year - b.year);
}

function formatValue(value: number): string {
  return value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

function formatPercent(value: number): string {
  return `${formatValue(value)}%`;
}

function EconomicContextPage() {
  const [gdpObservations, setGdpObservations] = useState<
    IndicatorObservation[]
  >([]);
  const [growthObservations, setGrowthObservations] = useState<
    IndicatorObservation[]
  >([]);
  const [wbesMetadata, setWbesMetadata] =
    useState<WBESMetadata | null>(null);
  const [businessObstacles, setBusinessObstacles] = useState<
    BusinessObstacle[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const [
          gdpData,
          growthData,
          metadata,
          obstacleData,
        ] = await Promise.all([
          fetchObservations(GDP_PER_CAPITA),
          fetchObservations(GDP_PER_CAPITA_GROWTH),
          fetchWBESMetadata(),
          fetchBusinessObstacles(),
        ]);

        if (!cancelled) {
          setGdpObservations(gdpData.results);
          setGrowthObservations(growthData.results);
          setWbesMetadata(metadata);
          setBusinessObstacles(obstacleData.results);
        }
      } catch {
        if (!cancelled) {
          setError(
            "Could not load the economic context data. Check that the API server is running and the WDI and WBES endpoints are available.",
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

  const gdpChartData = useMemo(
    () => toChartData(gdpObservations),
    [gdpObservations],
  );

  const growthChartData = useMemo(
    () => toChartData(growthObservations),
    [growthObservations],
  );

  const gdpValidCount = gdpChartData.filter(
    (item) => item.value !== null,
  ).length;

  const growthValidCount = growthChartData.filter(
    (item) => item.value !== null,
  ).length;

  const rankedObstacles = useMemo(
    () =>
      [...businessObstacles]
        .filter(
          (obstacle) =>
            Number.isFinite(obstacle.weighted_share) &&
            obstacle.valid_responses > 0,
        )
        .sort(
          (a, b) => b.weighted_share - a.weighted_share,
        ),
    [businessObstacles],
  );

  const topObstacles = rankedObstacles.slice(0, 5);

  const totalValidResponses = wbesMetadata
    ? businessObstacles.reduce(
        (total, obstacle) =>
          total + obstacle.valid_responses,
        0,
      )
    : 0;

  if (loading) {
    return (
      <main className="economic-context-page">
        <p role="status">Loading economic context data...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="economic-context-page">
        <p className="economic-context-error" role="alert">
          {error}
        </p>
        <button
          type="button"
          onClick={() => window.location.reload()}
        >
          Reload page
        </button>
      </main>
    );
  }

  return (
    <main className="economic-context-page">
      <header className="economic-context-header">
        <p className="economic-context-eyebrow">
          NEPAL · ECONOMIC DATA
        </p>
        <h1>Nepal's economic context</h1>
        <p>
          Explore Nepal's long-run economic indicators alongside
          constraints reported by businesses in the 2023 Enterprise Survey.
        </p>
      </header>

      <section
        className="economic-context-section"
        aria-labelledby="gdp-heading"
      >
        <h2 id="gdp-heading">GDP per capita</h2>
        <p>
          GDP per capita in constant 2015 US dollars. Using constant
          prices helps distinguish changes in real output per person
          from changes caused by inflation.
        </p>
        <p className="economic-context-count">
          {gdpValidCount} valid observations out of {gdpChartData.length}
        </p>

        {gdpValidCount === 0 ? (
          <p>No valid GDP per-capita observations are available.</p>
        ) : (
          <div className="economic-context-chart">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={gdpChartData}>
                <CartesianGrid
                  stroke="#e5e8e5"
                  vertical={false}
                />
                <XAxis
                  dataKey="year"
                  type="number"
                  domain={["dataMin", "dataMax"]}
                  tickLine={false}
                  axisLine={{ stroke: "#d7ddd8" }}
                  minTickGap={35}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  width={75}
                  tickFormatter={(value) =>
                    Number(value).toLocaleString()
                  }
                />
                <Tooltip
                  formatter={(value) =>
                    value == null
                      ? ["No data", "GDP per capita"]
                      : [
                          `$${formatValue(Number(value))}`,
                          "GDP per capita",
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

      <section
        className="economic-context-section"
        aria-labelledby="growth-heading"
      >
        <h2 id="growth-heading">
          Annual GDP per-capita growth
        </h2>
        <p>
          Annual percentage change in GDP per capita. Positive and
          negative values indicate growth and contraction, respectively.
        </p>
        <p className="economic-context-count">
          {growthValidCount} valid observations out of{" "}
          {growthChartData.length}
        </p>

        {growthValidCount === 0 ? (
          <p>No valid growth observations are available.</p>
        ) : (
          <div className="economic-context-chart">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={growthChartData}>
                <CartesianGrid
                  stroke="#e5e8e5"
                  vertical={false}
                />
                <XAxis
                  dataKey="year"
                  type="number"
                  domain={["dataMin", "dataMax"]}
                  tickLine={false}
                  axisLine={{ stroke: "#d7ddd8" }}
                  minTickGap={35}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  width={65}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  formatter={(value) =>
                    value == null
                      ? ["No data", "Annual growth"]
                      : [
                          formatPercent(Number(value)),
                          "Annual growth",
                        ]
                  }
                  labelFormatter={(year) => `Year: ${year}`}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#547f9b"
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

      <section
        className="economic-context-section"
        aria-labelledby="business-heading"
      >
        <div className="economic-context-section-heading">
          <div>
            <p className="economic-context-eyebrow">
              ENTERPRISE SURVEY · {wbesMetadata?.survey_period}
            </p>
            <h2 id="business-heading">
              What businesses reported
            </h2>
          </div>
          <Link
            className="economic-context-link"
            to="/business-environment"
          >
            Explore full survey analysis →
          </Link>
        </div>

        <p>
          The following obstacles are ordered by their survey-weighted
          share of valid responses rated as a major or severe obstacle.
        </p>

        {topObstacles.length === 0 ? (
          <p>
            No valid business-obstacle results are available.
          </p>
        ) : (
          <>
            <div className="economic-context-chart">
              <ResponsiveContainer
                width="100%"
                height={Math.max(260, topObstacles.length * 54)}
              >
                <BarChart
                  data={topObstacles}
                  layout="vertical"
                  margin={{
                    top: 4,
                    right: 30,
                    left: 12,
                    bottom: 4,
                  }}
                >
                  <CartesianGrid
                    stroke="#e5e8e5"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    domain={[0, "auto"]}
                    tickFormatter={(value) => `${value}%`}
                    tickLine={false}
                    axisLine={{ stroke: "#d7ddd8" }}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={155}
                    tick={{
                      fill: "#656b66",
                      fontSize: 12,
                    }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    formatter={(value) =>
                      value == null
                        ? ["No data", "Weighted share"]
                        : [
                            formatPercent(Number(value)),
                            "Weighted share",
                          ]
                    }
                  />
                  <Bar
                    dataKey="weighted_share"
                    name="Weighted share"
                    fill="#29513d"
                    radius={[0, 3, 3, 0]}
                    isAnimationActive={false}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="economic-context-table-wrapper">
              <table className="economic-context-table">
                <thead>
                  <tr>
                    <th scope="col">Business obstacle</th>
                    <th scope="col">Major/severe share</th>
                    <th scope="col">Valid responses</th>
                    <th scope="col">Excluded responses</th>
                  </tr>
                </thead>
                <tbody>
                  {topObstacles.map((obstacle) => (
                    <tr key={obstacle.obstacle}>
                      <td>{obstacle.label}</td>
                      <td>
                        {formatPercent(obstacle.weighted_share)}
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
          </>
        )}

        <div className="economic-context-survey-summary">
          <div>
            <p className="economic-context-summary-label">
              Survey
            </p>
            <p className="economic-context-summary-value">
              {wbesMetadata?.survey ?? "World Bank Enterprise Surveys"}
            </p>
          </div>
          <div>
            <p className="economic-context-summary-label">
              Survey period
            </p>
            <p className="economic-context-summary-value">
              {wbesMetadata?.survey_period ?? "Not available"}
            </p>
          </div>
          <div>
            <p className="economic-context-summary-label">
              Population covered
            </p>
            <p className="economic-context-summary-value">
              {wbesMetadata?.population_covered ?? "Not available"}
            </p>
          </div>
          <div>
            <p className="economic-context-summary-label">
              Valid-response records across obstacle measures
            </p>
            <p className="economic-context-summary-value">
              {totalValidResponses.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="economic-context-methodology">
          <h3>How to interpret these results</h3>
          <p>
            The displayed percentages are survey-weighted estimates,
            not simple counts of firms. Weighting helps account for
            the survey's sampling design.
          </p>
          <p>
            Each obstacle has its own valid-response and excluded-response
            counts. The sum of valid responses across obstacles is not the
            number of unique businesses because a business can answer
            multiple obstacle questions.
          </p>

          {wbesMetadata?.weighting && (
            <p>
              <strong>Weighting:</strong>{" "}
              Primary weight: {wbesMetadata.weighting.primary_weight}.
              {" "}Weighted measure:{" "}
              {wbesMetadata.weighting.weighted_share}.
            </p>
          )}

          {wbesMetadata?.limitations &&
            wbesMetadata.limitations.length > 0 && (
              <>
                <h3>Survey limitations</h3>
                <ul>
                  {wbesMetadata.limitations.map(
                    (limitation, index) => (
                      <li key={`${index}-${limitation}`}>
                        {limitation}
                      </li>
                    ),
                  )}
                </ul>
              </>
            )}
        </div>
      </section>

      <section
        className="economic-context-section economic-context-interpretation"
        aria-labelledby="interpretation-heading"
      >
        <h2 id="interpretation-heading">
          Reading the two datasets together
        </h2>
        <p>
          The WDI series describes national economic outcomes over
          many years. The Enterprise Survey captures reported
          constraints among eligible businesses during a specific
          survey period.
        </p>
        <p>
          These data provide complementary context, but they do not
          demonstrate that any particular business obstacle caused
          Nepal's historical growth pattern. Establishing causation
          would require a separate research design and additional evidence.
        </p>
      </section>
    </main>
  );
}

export default EconomicContextPage;
