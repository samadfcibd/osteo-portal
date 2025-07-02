import React, { useState, useCallback } from 'react';

// Subcomponents
const StarRating = ({ rating, maxRating = 5, interactive = false, onRatingChange = null }) => {
    const [hoverRating, setHoverRating] = useState(0);

    const displayRating = Number(rating?.average_rating ?? rating ?? 0);
    const reviewCount = rating?.review_count || 0;

    if (!interactive && displayRating === 0) {
        return <span className="text-muted">No ratings yet</span>;
    }

    const handleStarClick = useCallback((starIndex) => {
        if (interactive && onRatingChange) {
            onRatingChange(starIndex);
        }
    }, [interactive, onRatingChange]);

    return (
        <div className="d-flex align-items-center">
            {Array.from({ length: maxRating }, (_, index) => {
                const starIndex = index + 1;
                const isActive = interactive
                    ? (hoverRating || rating) >= starIndex
                    : displayRating >= starIndex;

                return (
                    <i
                        key={index}
                        className={`bi bi-star${isActive ? '-fill' : ''} ${interactive ? 'text-primary' : 'text-warning'}`}
                        style={{
                            fontSize: '0.8rem',
                            cursor: interactive ? 'pointer' : 'default'
                        }}
                        onClick={() => handleStarClick(starIndex)}
                        onMouseEnter={interactive ? () => setHoverRating(starIndex) : undefined}
                        onMouseLeave={interactive ? () => setHoverRating(0) : undefined}
                    />
                );
            })}
            {!interactive && displayRating > 0 && (
                <span className="ms-1 text-muted" style={{ fontSize: '0.8rem' }}>
                    ({displayRating.toFixed(1)}/{maxRating})
                    {reviewCount > 0 && ` • ${reviewCount} review${reviewCount !== 1 ? 's' : ''}`}
                </span>
            )}
        </div>
    );
};

export default StarRating;