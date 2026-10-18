
export interface AnnualObservation {
  year: number;
  value: string | number | null;
}

export interface AnnualChange {
  year: number;
  value: number | null;
  absoluteChange: number | null;
  percentageChange: number | null;
}

function parseValue(
  value: AnnualObservation["value"],
): number | null {
  if (value === null || value === "") {
    return null;
  }

  const parsed = Number(value);

  return Number.isFinite(parsed) ? parsed : null;
}

export function calculateAnnualChanges(
  observations: AnnualObservation[],
): AnnualChange[] {
  const chronological = observations
    .map((observation) => ({
      year: observation.year,
      value: parseValue(observation.value),
    }))
    .sort((a, b) => a.year - b.year);

  return chronological.map((observation, index) => {
    const previous =
      index > 0 ? chronological[index - 1] : null;

    const consecutiveYears =
      previous !== null &&
      observation.year === previous.year + 1;

    const validValues =
      previous !== null &&
      previous.value !== null &&
      observation.value !== null;

    const canCalculate =
      consecutiveYears && validValues;

    const absoluteChange =
      canCalculate
        ? observation.value! - previous!.value!
        : null;

    const percentageChange =
      canCalculate && previous!.value !== 0
        ? (absoluteChange! / Math.abs(previous!.value!)) * 100
        : null;

    return {
      year: observation.year,
      value: observation.value,
      absoluteChange,
      percentageChange,
    };
  });
}
