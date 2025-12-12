interface ScoreGaugeProps {
  score: number;
}

export function ScoreGauge({ score }: ScoreGaugeProps) {
  const percentage = Math.min(Math.max(score, 0), 100);
  const angle = (percentage / 100) * 180 - 90; // -90 to 90 degrees

  const getColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="flex flex-col items-center">
      <div className={`relative w-32 h-16 ${getBgColor(score)} rounded-t-full overflow-hidden`}>
        <div
          className="absolute bottom-0 left-1/2 w-1 h-8 bg-gray-300 origin-bottom transform -translate-x-1/2"
          style={{
            transform: `translateX(-50%) rotate(${angle}deg)`,
          }}
        />
        <div className="absolute bottom-0 left-1/2 w-2 h-2 bg-gray-600 rounded-full transform -translate-x-1/2 translate-y-1/2" />
      </div>
      <div className="mt-4 text-center">
        <div className={`text-4xl font-bold ${getColor(score)}`}>
          {percentage}
        </div>
        <div className="text-sm text-gray-600">out of 100</div>
      </div>
    </div>
  );
}