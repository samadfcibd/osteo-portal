
import { Modal, Button } from 'react-bootstrap';
import StarRating from './StarRating';

const ReviewsModal = ({ show, onHide, reviews }) => (
    <Modal show={show} onHide={onHide} size="lg">
        <Modal.Header className='bg-primary text-white' closeButton>
            <Modal.Title>
                <i className="bi bi-chat-square-text me-2"></i>
                User Reviews
            </Modal.Title>
        </Modal.Header>
        <Modal.Body>
            {Array.isArray(reviews) && reviews.length > 0 ? (
                <div className="list-group">
                    {reviews.map((review, index) => (
                        <div key={index} className="list-group-item">
                            <div className="d-flex justify-content-between mb-2">
                                <StarRating rating={review.rating} maxRating={5} />
                                <small className="text-muted">
                                    {new Date(review.created_at).toLocaleDateString()}
                                </small>
                            </div>
                            {review.review && <p className="mb-2">{review.review}</p>}
                            <div className="d-flex justify-content-between">
                                <small className="text-muted">
                                    {review.reviewer_name || 'Anonymous'}
                                </small>
                                {review.reviewer_email && review.reviewer_email !== 'Anonymous' && (
                                    <small className="text-muted">{review.reviewer_email}</small>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="alert alert-info">
                    No reviews yet for this organism.
                </div>
            )}
        </Modal.Body>
        <Modal.Footer>
            <Button variant="secondary" onClick={onHide}>
                Close
            </Button>
        </Modal.Footer>
    </Modal>
);

export default ReviewsModal;