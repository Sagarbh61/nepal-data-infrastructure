
import { useEffect, useMemo, useState } from "react";
import {Link} from 'react-router';
import {
  fetchPopulation,
  type LocalGovernmentPopulation,
} from "../services/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./PopulationPage.css";

const numberFormat = new Intl.NumberFormat("en-US");

const chartColors = {
  primary: "#397653",
  secondary: "#8CB8A0",
};

type SortField =
  | "population_total"
  | "population_male"
  | "population_female"
  | "households";

function PopulationPage() {
  const [records, setRecords] = useState<LocalGovernmentPopulation[]>([]);
  const [province, setProvince] = useState("");
  const [district, setDistrict] = useState("");
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("population_total");
  const [sortDirection, setSortDirection] = useState<"desc" | "asc">("desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadPopulation() {
      setLoading(true);
      setError("");

      try {
        const response = await fetchPopulation({ census_year: 2021 });

        if (!cancelled) {
          setRecords(response.results);
        }
      } catch {
        if (!cancelled) {
          setError(
            "Could not load population data. Check that the Django API is running.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadPopulation();

    return () => {
      cancelled = true;
    };
  }, []);

  const provinces = useMemo(() => {
    const unique = new Map<number, string>();

    for (const record of records) {
      unique.set(record.province_code, record.province_name);
    }

    return Array.from(unique.entries())
      .sort(([a], [b]) => a - b)
      .map(([code, name]) => ({ code, name }));
  }, [records]);

  const districts = useMemo(() => {
    const unique = new Map<
      string,
      {
        provinceCode: number;
        districtCode: number;
        name: string;
      }
    >();

    for (const record of records) {
      if (province && record.province_code !== Number(province)) {
        continue;
      }

      const key = `${record.province_code}:${record.district_code}`;

      unique.set(key, {
        provinceCode: record.province_code,
        districtCode: record.district_code,
        name: record.district_name,
      });
    }

    return Array.from(unique.entries())
      .sort(([, a], [, b]) => a.name.localeCompare(b.name))
      .map(([key, value]) => ({ key, ...value }));
  }, [records, province]);

  // National province comparison: unaffected by the active filters.
  const provincePopulation = useMemo(() => {
    const totals = new Map<
      number,
      { name: string; population: number }
    >();

    for (const record of records) {
      const existing = totals.get(record.province_code);

      if (existing) {
        existing.population += record.population_total;
      } else {
        totals.set(record.province_code, {
          name: record.province_name,
          population: record.population_total,
        });
      }
    }

    return Array.from(totals.values()).sort(
      (a, b) => b.population - a.population,
    );
  }, [records]);

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLowerCase();

    return records
      .filter((record) => {
        if (province && record.province_code !== Number(province)) {
          return false;
        }

        if (district) {
          const [districtProvinceCode, districtCode] = district
            .split(":")
            .map(Number);

          if (
            record.province_code !== districtProvinceCode ||
            record.district_code !== districtCode
          ) {
            return false;
          }
        }

        if (!query) return true;

        return (
          record.local_government_name.toLowerCase().includes(query) ||
          record.district_name.toLowerCase().includes(query) ||
          record.province_name.toLowerCase().includes(query)
        );
      })
      .sort((a, b) => {
        const difference = a[sortBy] - b[sortBy];
        return sortDirection === "desc" ? -difference : difference;
      });
  }, [records, province, district, search, sortBy, sortDirection]);

  const summary = useMemo(() => {
    return filteredRecords.reduce(
      (totals, record) => ({
        population: totals.population + record.population_total,
        male: totals.male + record.population_male,
        female: totals.female + record.population_female,
        households: totals.households + record.households,
      }),
      { population: 0, male: 0, female: 0, households: 0 },
    );
  }, [filteredRecords]);

  const averageHouseholdSize =
    summary.households > 0
      ? summary.population / summary.households
      : 0;

  const sexComposition = [
    { name: "Male", value: summary.male },
    { name: "Female", value: summary.female },
  ];

  function handleProvinceChange(value: string) {
    setProvince(value);
    setDistrict("");
  }

  function handleSortChange(value: SortField) {
    if (sortBy === value) {
      setSortDirection((current) => (current === "desc" ? "asc" : "desc"));
    } else {
      setSortBy(value);
      setSortDirection("desc");
    }
  }

  function resetFilters() {
    setProvince("");
    setDistrict("");
    setSearch("");
    setSortBy("population_total");
    setSortDirection("desc");
  }

  function sortIndicator(field: SortField) {
    if (sortBy !== field) return "";
    return sortDirection === "desc" ? " ↓" : " ↑";
  }

  return (
    <main className="population-page">
          <Link className="detail-back-link" to="/explore">
                  ← Back to Explore Data
                </Link>
      <header className="population-header">

        <h1>Nepal Population Dashboard</h1>
        <p>
          Understand Nepal's population distribution, compare provinces,
          and explore household and population composition across local
          governments.
        </p>
        <span className="census-badge">
          National Population and Housing Census 2021
        </span>
      </header>

      {loading && (
        <p className="population-status">Loading census records…</p>
      )}

      {!loading && error && (
        <p className="population-status population-error">{error}</p>
      )}

      {!loading && !error && (
        <>
          <section
            className="population-overview"
            aria-label="Selected population summary"
          >
            <article className="population-stat">
              <p>Total population</p>
              <strong>{numberFormat.format(summary.population)}</strong>
              <span>People in selected areas</span>
            </article>

            <article className="population-stat">
              <p>Households</p>
              <strong>{numberFormat.format(summary.households)}</strong>
              <span>Reported households</span>
            </article>

            <article className="population-stat">
              <p>Male population</p>
              <strong>{numberFormat.format(summary.male)}</strong>
              <span>
                {summary.population
                  ? `${((summary.male / summary.population) * 100).toFixed(1)}% of total`
                  : "No records"}
              </span>
            </article>

            <article className="population-stat">
              <p>Female population</p>
              <strong>{numberFormat.format(summary.female)}</strong>
              <span>
                {summary.population
                  ? `${((summary.female / summary.population) * 100).toFixed(1)}% of total`
                  : "No records"}
              </span>
            </article>
          </section>

          <section
            className="population-charts"
            aria-label="Population analysis"
          >
            <div className="population-section-heading">
              <div>
                <h2>Population at a glance</h2>
                <p>
                  Compare population across provinces and examine the sex
                  composition of the selected areas.
                </p>
              </div>
            </div>

            <div className="population-chart-grid">
              <article className="population-chart-card">
                <div className="population-chart-heading">
                  <h3>Population by province</h3>
                  <p>2021 census · Ranked by total population</p>
                </div>

                {provincePopulation.length > 0 ? (
                  <div className="population-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={provincePopulation}
                        layout="vertical"
                        margin={{
                          top: 8,
                          right: 24,
                          bottom: 8,
                          left: 12,
                        }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          horizontal={false}
                        />
                        <XAxis
                          type="number"
                          tickFormatter={(value: number) =>
                            `${(value / 1_000_000).toFixed(1)}M`
                          }
                          fontSize={12}
                        />
                        <YAxis
                          type="category"
                          dataKey="name"
                          width={105}
                          fontSize={11}
                          tickLine={false}
                        />
                        <Tooltip
                          formatter={(value) => [
                            numberFormat.format(Number(value)),
                            "Population",
                          ]}
                        />
                        <Bar
                          dataKey="population"
                          name="Population"
                          fill={chartColors.primary}
                          radius={[0, 4, 4, 0]}
                          maxBarSize={28}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="population-empty">
                    No province data is available.
                  </p>
                )}

                <p className="population-chart-note">
                  Calculated by summing local-government records. This chart
                  remains a national comparison when filters change.
                </p>
              </article>

              <article className="population-chart-card">
                <div className="population-chart-heading">
                  <h3>Population by sex</h3>
                  <p>Based on the currently selected records</p>
                </div>

                {summary.population > 0 ? (
                  <>
                    <div className="population-chart population-sex-chart">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sexComposition}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="45%"
                            innerRadius={65}
                            outerRadius={100}
                            paddingAngle={3}
                          >
                            <Cell fill={chartColors.primary} />
                            <Cell fill={chartColors.secondary} />
                          </Pie>
                          <Tooltip
                            formatter={(value) => [
                              numberFormat.format(Number(value)),
                              "People",
                            ]}
                          />
                          <Legend verticalAlign="bottom" />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="population-sex-breakdown">
                      <div>
                        <span className="population-dot male-dot" />
                        <span>Male</span>
                        <strong>
                          {(
                            (summary.male / summary.population) *
                            100
                          ).toFixed(1)}
                          %
                        </strong>
                      </div>
                      <div>
                        <span className="population-dot female-dot" />
                        <span>Female</span>
                        <strong>
                          {(
                            (summary.female / summary.population) *
                            100
                          ).toFixed(1)}
                          %
                        </strong>
                      </div>
                    </div>
                  </>
                ) : (
                  <p className="population-empty">
                    No records match the current filters.
                  </p>
                )}
              </article>

              <article className="population-chart-card population-household-card">
                <div className="population-chart-heading">
                  <h3>Average household size</h3>
                  <p>People per reported household</p>
                </div>

                <div className="population-household-value">
                  {summary.households > 0
                    ? averageHouseholdSize.toFixed(2)
                    : "—"}
                </div>

                <p className="population-chart-note">
                  Calculated as selected population divided by selected
                  households. This is an average, not the household-size
                  distribution.
                </p>
              </article>
            </div>
          </section>

          <section className="population-explorer-section">
            <div className="population-section-heading">
              <div>
                <h2>Explore local governments</h2>
                <p>
                  Filter by geography, search names, or sort by population
                  and household counts.
                </p>
              </div>

              <span className="population-record-count">
                {numberFormat.format(filteredRecords.length)} of{" "}
                {numberFormat.format(records.length)} records
              </span>
            </div>

            <div className="population-filters">
              <div className="population-filter">
                <label htmlFor="population-province">Province</label>
                <select
                  id="population-province"
                  value={province}
                  onChange={(event) =>
                    handleProvinceChange(event.target.value)
                  }
                >
                  <option value="">All provinces</option>
                  {provinces.map((item) => (
                    <option key={item.code} value={item.code}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="population-filter">
                <label htmlFor="population-district">District</label>
                <select
                  id="population-district"
                  value={district}
                  onChange={(event) => setDistrict(event.target.value)}
                >
                  <option value="">All districts</option>
                  {districts.map((item) => (
                    <option key={item.key} value={item.key}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="population-filter population-search">
                <label htmlFor="population-search">Search locations</label>
                <input
                  id="population-search"
                  type="search"
                  placeholder="Local government or district…"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>

              <button
                className="population-reset"
                type="button"
                onClick={resetFilters}
              >
                Reset filters
              </button>
            </div>

            <div className="population-table-wrapper">
              <table className="population-table">
                <thead>
                  <tr>
                    <th scope="col">Local government</th>
                    <th scope="col">District</th>
                    <th scope="col">Province</th>
                    <th scope="col">
                      <button
                        type="button"
                        onClick={() =>
                          handleSortChange("population_total")
                        }
                      >
                        Total population{sortIndicator("population_total")}
                      </button>
                    </th>
                    <th scope="col">
                      <button
                        type="button"
                        onClick={() =>
                          handleSortChange("population_male")
                        }
                      >
                        Male{sortIndicator("population_male")}
                      </button>
                    </th>
                    <th scope="col">
                      <button
                        type="button"
                        onClick={() =>
                          handleSortChange("population_female")
                        }
                      >
                        Female{sortIndicator("population_female")}
                      </button>
                    </th>
                    <th scope="col">
                      <button
                        type="button"
                        onClick={() => handleSortChange("households")}
                      >
                        Households{sortIndicator("households")}
                      </button>
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {filteredRecords.map((record) => (
                    <tr
                      key={`${record.census_year}-${record.province_code}-${record.district_code}-${record.local_government_code}`}
                    >
                      <td className="population-location-name">
                        {record.local_government_name}
                      </td>
                      <td>{record.district_name}</td>
                      <td>{record.province_name}</td>
                      <td>
                        {numberFormat.format(record.population_total)}
                      </td>
                      <td>
                        {numberFormat.format(record.population_male)}
                      </td>
                      <td>
                        {numberFormat.format(record.population_female)}
                      </td>
                      <td>{numberFormat.format(record.households)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredRecords.length === 0 && (
                <p className="population-empty">
                  No local governments match these filters.
                </p>
              )}
            </div>
          </section>

          <section className="population-methodology">
            <p className="eyebrow">DATA NOTES</p>
            <h2>Source and methodology</h2>
            <p>
              Source: Nepal National Population and Housing Census 2021.
              Population figures describe the census reference period,
              not present-day estimates.
            </p>
            <p>
              Summary figures and sex composition are calculated from the
              local-government records matching the current filters. Male
              and female shares use the selected total population as the
              denominator.
            </p>
            <p>
              Province chart totals are calculated independently from all
              loaded local-government records. District and province
              aggregates from the raw census file are not included, avoiding
              double-counting.
            </p>
            <p>
              Average household size is calculated as population divided
              by reported households. The data does not provide a household
              size distribution in this dataset.
            </p>
          </section>
        </>
      )}
    </main>
  );
}

export default PopulationPage;
