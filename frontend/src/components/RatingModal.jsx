import React, { useCallback } from 'react';
import { Spinner, Modal, Button } from 'react-bootstrap';
import StarRating from './StarRating';

const RatingModal = ({
    show,
    onHide,
    organism,
    ratingState,
    onRatingStateChange,
    onSubmit,
    isSubmitting
}) => {
    const handleInputChange = useCallback((field, value) => {
        onRatingStateChange(prev => ({ ...prev, [field]: value }));
    }, [onRatingStateChange]);

    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header className='bg-success text-white' closeButton>
                <Modal.Title>
                    <i className="bi bi-star me-2"></i>
                    Rate {organism?.organism_name}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <div className="text-center mb-4">
                    <h6 className="mb-3">How would you rate this organism?</h6>
                    <StarRating
                        rating={ratingState.userRating}
                        interactive={true}
                        onRatingChange={(rating) => handleInputChange('userRating', rating)}
                    />
                    {ratingState.userRating > 0 && (
                        <p className="text-muted mt-2">
                            You selected: {ratingState.userRating} star{ratingState.userRating !== 1 ? 's' : ''}
                        </p>
                    )}
                </div>

                <div className="mb-3">
                    <label htmlFor="userName" className="form-label">Your Name (Optional)</label>
                    <input
                        type="text"
                        id="userName"
                        className="form-control"
                        placeholder="John Doe"
                        value={ratingState.userName}
                        onChange={(e) => handleInputChange('userName', e.target.value)}
                    />
                </div>

                <div className="mb-3">
                    <label htmlFor="userEmail" className="form-label">Your Email (Optional)</label>
                    <input
                        type="email"
                        id="userEmail"
                        className="form-control"
                        placeholder="john@example.com"
                        value={ratingState.userEmail}
                        onChange={(e) => handleInputChange('userEmail', e.target.value)}
                    />
                </div>

                <div className="mb-3">
                    <label htmlFor="reviewText" className="form-label">Review (Optional)</label>
                    <textarea
                        id="reviewText"
                        className="form-control"
                        rows="3"
                        placeholder="Share your experience with this organism..."
                        value={ratingState.userReview}
                        onChange={(e) => handleInputChange('userReview', e.target.value)}
                    />
                </div>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide} disabled={isSubmitting}>
                    Cancel
                </Button>
                <Button
                    variant="primary"
                    onClick={onSubmit}
                    disabled={ratingState.userRating === 0 || isSubmitting}
                >
                    {isSubmitting ? (
                        <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Submitting...
                        </>
                    ) : (
                        <>
                            <i className="bi bi-check-lg me-1"></i>
                            Submit Rating
                        </>
                    )}
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default RatingModal;