
const DEFAULT_API_BASE_URL = import.meta.env.PROD
  ? "https://nepal-data-infrastructure-psi.vercel.app/api"
  : "http://127.0.0.1:8000/api";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/$/, "");



export interface LocalGovernmentPopulation {
  census_year: number;
  province_code: number;
  district_code: number;
  local_government_code: number;
  province_name: string;
  district_name: string;
  local_government_name: string;
  households: number;
  population_total: number;
  population_male: number;
  population_female: number;
}


export interface Indicator {
  code: string;
  name: string;
  source: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export async function fetchIndicators(
  page = 1,
): Promise<PaginatedResponse<Indicator>> {
  const response = await fetch(
    `${API_BASE_URL}/indicators/?page=${page}`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load indicators (${response.status})`);
  }

  return response.json() as Promise<PaginatedResponse<Indicator>>;
}

export interface IndicatorObservation {
  indicator_code: string;
  country_code: string;
  year: number;
  value: string | null;
}

export async function fetchIndicator(
  code: string,
): Promise<Indicator> {
  const response = await fetch(
    `${API_BASE_URL}/indicators/${encodeURIComponent(code)}/`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load indicator (${response.status})`);
  }

  return response.json() as Promise<Indicator>;
}

export async function fetchObservations(
  indicatorCode: string,
  countryCode = "NPL",
): Promise<PaginatedResponse<IndicatorObservation>> {
  const params = new URLSearchParams({
    indicator_code: indicatorCode,
    country_code: countryCode,
  });

  let nextUrl: string | null =
    `${API_BASE_URL}/observations/?${params.toString()}`;

  let totalCount = 0;
  let previous: string | null = null;

  const allObservations: IndicatorObservation[] = [];

  while (nextUrl !== null) {
    const response = await fetch(nextUrl);

    if (!response.ok) {
      throw new Error(
        `Failed to load observations (${response.status})`,
      );
    }

    const page =
      (await response.json()) as PaginatedResponse<IndicatorObservation>;

    totalCount = page.count;
    previous = page.previous;
    allObservations.push(...page.results);

    // Follow the API-provided link until there are no more pages.
    nextUrl = page.next;
  }

  return {
    count: totalCount,
    next: null,
    previous,
    results: allObservations,
  };
}



export async function fetchPopulation(
  filters: {
    census_year?: number;
    province_code?: number;
    district_code?: number;
    local_government_code?: number;
  } = {},
): Promise<PaginatedResponse<LocalGovernmentPopulation>> {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined) {
      params.set(key, String(value));
    }
  }

  let nextUrl: string | null =
    `${API_BASE_URL}/population/?${params.toString()}`;

  let totalCount = 0;
  let previous: string | null = null;
  const allRecords: LocalGovernmentPopulation[] = [];

  while (nextUrl !== null) {
    const response = await fetch(nextUrl);

    if (!response.ok) {
      throw new Error(
        `Failed to load population data (${response.status})`,
      );
    }

    const page =
      (await response.json()) as PaginatedResponse<LocalGovernmentPopulation>;

    totalCount = page.count;
    previous = page.previous;
    allRecords.push(...page.results);

    nextUrl = page.next;
  }

  return {
    count: totalCount,
    next: null,
    previous,
    results: allRecords,
  };
}

export interface WBESMetadata {
  survey: string;
  survey_period: string;
  population_covered: string;
  measure: string;
  weighting: {
    primary_weight: string;
    weighted_share: string;
    unweighted_share: string;
  };
  limitations: string[];
}

export interface BusinessObstacle {
  obstacle: string;
  label: string;
  weight: string;
  total_records: number;
  valid_responses: number;
  excluded_responses: number;
  major_or_severe_responses: number;
  unweighted_share: number;
  weighted_share: number;
}

export async function fetchWBESMetadata(): Promise<WBESMetadata> {
  const response = await fetch(`${API_BASE_URL}/wbes/metadata/`);

  if (!response.ok) {
    throw new Error(`Failed to load WBES metadata (${response.status})`);
  }

  return response.json() as Promise<WBESMetadata>;
}

export async function fetchBusinessObstacles(): Promise<
  PaginatedResponse<BusinessObstacle>
> {
  const response = await fetch(`${API_BASE_URL}/wbes/business-obstacles/`);

  if (!response.ok) {
    throw new Error(`Failed to load business obstacles (${response.status})`);
  }

  return response.json() as Promise<PaginatedResponse<BusinessObstacle>>;
}
