const API_BASE_URL = "http://127.0.0.1:8000/api";

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
