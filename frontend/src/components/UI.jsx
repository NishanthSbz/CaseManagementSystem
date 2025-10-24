// Status badge component
export const StatusBadge = ({ status }) => {
  const getStatusStyle = (status) => {
    switch (status) {
      case 'open':
        return 'badge-info';
      case 'in_progress':
        return 'badge-warning';
      case 'closed':
        return 'badge-success';
      default:
        return 'badge-info';
    }
  };

  return (
    <span className={`badge ${getStatusStyle(status)}`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};

// Priority badge component
export const PriorityBadge = ({ priority }) => {
  const getPriorityStyle = (priority) => {
    switch (priority) {
      case 'low':
        return 'badge-success';
      case 'medium':
        return 'badge-warning';
      case 'high':
        return 'badge-error';
      default:
        return 'badge-info';
    }
  };

  return (
    <span className={`badge ${getPriorityStyle(priority)}`}>
      {priority.toUpperCase()}
    </span>
  );
};

// Loading skeleton component
export const LoadingSkeleton = ({ className = '' }) => {
  return <div className={`loading-skeleton ${className}`}></div>;
};

// Card skeleton for loading states
export const CardSkeleton = () => {
  return (
    <div className="card animate-pulse">
      <div className="card-header">
        <LoadingSkeleton className="h-4 w-3/4 mb-2" />
        <LoadingSkeleton className="h-3 w-1/2" />
      </div>
      <div className="card-content">
        <LoadingSkeleton className="h-3 w-full mb-2" />
        <LoadingSkeleton className="h-3 w-2/3" />
      </div>
    </div>
  );
};

// Table skeleton for loading states
export const TableSkeleton = ({ rows = 5, cols = 4 }) => {
  return (
    <div className="animate-pulse">
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="flex space-x-4">
            {Array.from({ length: cols }).map((_, colIndex) => (
              <LoadingSkeleton
                key={colIndex}
                className="h-4 flex-1"
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};