import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Spinner, Pagination, Modal, Button } from 'react-bootstrap';

const ResourcesModal = ({
    showModal,
    setShowModal,
    selectedStage,
    selectedCountry,
    stages,
    countries
}) => {
    const [organisms, setOrganism] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showRatingModal, setShowRatingModal] = useState(false);
    const [selectedOrganism, setSelectedOrganism] = useState(null);
    const [userRating, setUserRating] = useState(0);
    const [userReview, setUserReview] = useState('');
    const [userName, setUserName] = useState('');
    const [userEmail, setUserEmail] = useState('');
    const [reviews, setReviews] = useState([]); // Initialize as empty array
    const [showReviewsModal, setShowReviewsModal] = useState(false);
    const [submittingRating, setSubmittingRating] = useState(false);
    const [pagination, setPagination] = useState({
        page: 1,
        per_page: 10,
        total: 0,
        total_pages: 0
    });

    const fetchReviews = async (organismId) => {
        try {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/organisms/${organismId}/reviews`);
            setReviews(response.data?.data?.reviews || []); // Ensure we always get an array
            setShowReviewsModal(true);
        } catch (error) {
            console.error('Error fetching reviews:', error);
            setReviews([]); // Reset to empty array on error
            alert('Failed to load reviews');
        }
    };

    // Function to get ratings from your database
    const getOrganismRating = async (organismId) => {
        try {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/organisms/${organismId}/rating`);
            return response.data.success ? response.data.rating : null;
        } catch (error) {
            console.warn(`Rating API error for organism ${organismId}:`, error);
            return null;
        }
    };

    // Function to submit rating
    const submitRating = async (organismId, rating, review = '', name = '', email = '') => {
        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/organisms/${organismId}/rating`, {
                rating,
                review,
                user_name: name,
                user_email: email
            });
            return response.data.success;
        } catch (error) {
            console.error('Error submitting rating:', error);
            throw error;
        }
    };

    const enrichWithGbifData = async (organismsList) => {
        const enriched = await Promise.all(
            organismsList.map(async (org) => {
                try {
                    let found = false;
                    let images = [];
                    let rating = null;

                    // Check if found in selected country
                    const occurrenceRes = await axios.get("https://api.gbif.org/v1/occurrence/search", {
                        params: {
                            scientificName: org.organism_name,
                            country: selectedCountry,
                            limit: 0
                        }
                    });
                    found = occurrenceRes.data.count > 0;

                    // Get 1–2 images
                    const imageRes = await axios.get("https://api.gbif.org/v1/occurrence/search", {
                        params: {
                            scientificName: org.organism_name,
                            mediaType: "StillImage",
                            limit: 2,
                            hasCoordinate: true,
                            hasGeospatialIssue: false
                        }
                    });

                    images = imageRes.data.results.flatMap(r => r.media?.map(m => m.identifier) || []);
                    const kingdom = imageRes?.data?.results?.[0]?.kingdom ?? org.organism_type;

                    // Get rating from your database
                    // rating = await getOrganismRating(org.organism_id);

                    return {
                        ...org,
                        gbifKingdom: kingdom,
                        gbifFound: found,
                        gbifImages: images,
                        // rating: rating
                    };

                } catch (error) {
                    console.warn(`GBIF error for ${org.organism_name}`, error);
                    return {
                        ...org,
                        gbifKingdom: org.organism_type,
                        gbifFound: false,
                        gbifImages: [],
                        // rating: null
                    };
                }
            })
        );
        return enriched;
    };

    // Fixed Rating component
    const StarRating = ({ rating, maxRating = 5, interactive = false, onRatingChange = null }) => {
        const [hoverRating, setHoverRating] = useState(0);

        // Handle case when rating is null or undefined
        const displayRating = Number(rating?.average_rating ?? rating ?? 0);
        const reviewCount = rating?.review_count || 0;

        if (!interactive && displayRating === 0) {
            return <span className="text-muted">No ratings yet</span>;
        }

        return (
            <div className="d-flex align-items-center">
                {[...Array(maxRating)].map((_, index) => {
                    const starIndex = index + 1;
                    const isActive = interactive
                        ? (hoverRating || userRating) >= starIndex
                        : displayRating >= starIndex;

                    return (
                        <i
                            key={index}
                            className={`bi bi-star${isActive ? '-fill' : ''} ${interactive ? 'text-primary' : 'text-warning'}`}
                            style={{
                                fontSize: '0.8rem',
                                cursor: interactive ? 'pointer' : 'default'
                            }}
                            onClick={interactive ? () => onRatingChange(starIndex) : undefined}
                            onMouseEnter={interactive ? () => setHoverRating(starIndex) : undefined}
                            onMouseLeave={interactive ? () => setHoverRating(0) : undefined}
                        ></i>
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

    const fetchOrganismList = async (page = 1) => {
        if (!selectedStage) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/organisms`, {
                params: {
                    stage: selectedStage,
                    page: page,
                    per_page: pagination.per_page
                }
            });

            if (response.data.success) {
                const enrichedOrganisms = await enrichWithGbifData(response.data.data);
                console.log(enrichedOrganisms)

                setOrganism(enrichedOrganisms);
                setPagination(response.data.pagination);
            } else {
                setError(response.data.message || 'Failed to fetch data');
            }
        } catch (err) {
            setError(err.message || 'An error occurred');
            console.error('Error fetching organisms:', err);
        } finally {
            setLoading(false);
        }
    };

    // Handle rating modal
    const openRatingModal = (organism) => {
        setSelectedOrganism(organism);
        setUserRating(0);
        setUserReview('');
        setShowRatingModal(true);
    };

    const handleRatingSubmit = async () => {
        if (!selectedOrganism || userRating === 0) {
            alert('Please select a rating before submitting.');
            return;
        }

        setSubmittingRating(true);
        try {
            await submitRating(
                selectedOrganism.organism_id,
                userRating,
                userReview,
                userName,
                userEmail
            );
            // Reset form
            setUserName('');
            setUserEmail('');
            setUserReview('');

            // Refresh the organism data to show updated rating
            await fetchOrganismList(pagination.page);

            setShowRatingModal(false);
            alert('Rating submitted successfully!');
        } catch (error) {
            alert('Failed to submit rating. Please try again.');
        } finally {
            setSubmittingRating(false);
        }
    };

    useEffect(() => {
        if (selectedStage && showModal) {
            fetchOrganismList();
        }
    }, [selectedStage, showModal, pagination.per_page]);

    const handlePageChange = (page) => {
        setPagination(prev => ({ ...prev, page }));
        fetchOrganismList(page);
    };

    const handlePerPageChange = (e) => {
        const newPerPage = parseInt(e.target.value);
        setPagination(prev => ({ ...prev, per_page: newPerPage, page: 1 }));
    };

    if (!showModal) return null;

    return (
        <>
            <div className={`modal fade ${showModal ? 'show' : ''}`}
                style={{ display: showModal ? 'block' : 'none' }}
                tabIndex="-1"
                role="dialog">
                <div className="modal-dialog modal-xl modal-dialog-centered" role="document">
                    <div className="modal-content">
                        <div className="modal-header bg-primary text-white">
                            <h5 className="modal-title">
                                <i className="bi bi-clipboard-data me-2"></i>
                                Available Resources
                            </h5>
                            <button
                                type="button"
                                className="btn-close btn-close-white"
                                onClick={() => setShowModal(false)}
                                disabled={loading}
                            ></button>
                        </div>

                        <div className="modal-body">
                            {loading && (
                                <div className="text-center py-4">
                                    <Spinner animation="border" variant="primary" />
                                    <p className="mt-2">Loading resources...</p>
                                </div>
                            )}

                            {error && (
                                <div className="alert alert-danger">
                                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                    {error}
                                </div>
                            )}

                            {!loading && !error && (
                                <>
                                    <div className="row mb-4">
                                        <div className="col-md-6">
                                            <div className="card bg-light">
                                                <div className="card-body text-center">
                                                    <i className="bi bi-clipboard-check display-6 text-primary mb-2"></i>
                                                    <h6 className="card-title">Selected Stage</h6>
                                                    <p className="card-text fw-bold text-primary">
                                                        {stages.find(s => s.stage_id == selectedStage)?.stage_name}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="card bg-light">
                                                <div className="card-body text-center">
                                                    <i className="bi bi-globe display-6 text-success mb-2"></i>
                                                    <h6 className="card-title">Selected Country</h6>
                                                    <p className="card-text fw-bold text-success">
                                                        {countries.find(c => c.value === selectedCountry)?.label}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-12">
                                            <h6 className="mb-2">
                                                <i className="bi bi-list-ul me-2"></i>
                                                Recommended Natural Resources:
                                            </h6>
                                            <hr />
                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-12">
                                            {organisms.length > 0 ? (
                                                <div className="table-responsive">
                                                    <table className="table table-hover align-middle">
                                                        <thead>
                                                            <tr>
                                                                <th className="bg-dark text-light">Organism</th>
                                                                <th className="bg-dark text-light">Food Sources</th>
                                                                <th className="bg-dark text-light">Patients Rating</th>
                                                                <th className="bg-dark text-light">Sample Image</th>
                                                                <th className="bg-dark text-light">Details</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {organisms.map(organism => (
                                                                <tr key={organism.data_id}>
                                                                    <td>
                                                                        <div className="d-flex align-items-center">
                                                                            <div>
                                                                                <h6 className="mb-0">{organism.organism_name}</h6>
                                                                                <small className={organism.gbifFound ? 'text-success' : organism.gbifFound === false ? 'text-danger' : 'text-muted'}>
                                                                                    {organism.gbifFound === undefined ? (
                                                                                        <span>
                                                                                            <i className="fas fa-spinner fa-spin me-1"></i> Checking...
                                                                                        </span>
                                                                                    ) : organism.gbifFound ? (
                                                                                        `✅ Found in your country`
                                                                                    ) : (
                                                                                        `❌ Not Found in your country`
                                                                                    )}
                                                                                </small>
                                                                            </div>
                                                                        </div>
                                                                    </td>
                                                                    <td>
                                                                        <div className="d-flex flex-wrap gap-1">
                                                                            <span className="badge bg-light text-dark">Turmeric</span>
                                                                            <span className="badge bg-light text-dark">Fish Oil</span>
                                                                            <span className="badge bg-light text-dark">Leafy Greens</span>
                                                                        </div>
                                                                    </td>
                                                                    <td>
                                                                        <StarRating rating={organism.rating} />
                                                                        <div className="d-flex gap-2 mt-1">
                                                                            <button
                                                                                className="btn btn-sm btn-outline-primary"
                                                                                onClick={() => openRatingModal(organism)}
                                                                            >
                                                                                <i className="bi bi-star me-1"></i>
                                                                                Rate
                                                                            </button>
                                                                            <button
                                                                                className="btn btn-sm btn-outline-secondary"
                                                                                onClick={() => fetchReviews(organism.organism_id)}
                                                                            >
                                                                                <i className="bi bi-chat-square-text me-1"></i>
                                                                                Reviews
                                                                            </button>
                                                                        </div>
                                                                    </td>
                                                                    <td>
                                                                        <div className="d-flex">
                                                                            {organism.gbifImages?.slice(0, 2).map((image, idx) => (
                                                                                <img
                                                                                    key={idx}
                                                                                    src={image}
                                                                                    alt={organism.organism_name}
                                                                                    className="rounded me-2"
                                                                                    style={{ width: '50px', height: '50px', objectFit: 'cover', cursor: 'pointer' }}
                                                                                    onClick={() => window.open(image, '_blank')}
                                                                                />
                                                                            ))}
                                                                            {organism.gbifImages?.length === 0 && (
                                                                                <span className="text-muted">No images found</span>
                                                                            )}
                                                                        </div>
                                                                    </td>
                                                                    <td>
                                                                        <small className="d-block mb-1">
                                                                            Organism Type: <i style={{ textTransform: 'capitalize' }}>
                                                                                {organism.gbifKingdom}
                                                                            </i>
                                                                        </small>
                                                                        <small className="d-block mb-1">
                                                                            Protein: <i style={{ textTransform: 'capitalize' }}>
                                                                                {organism.protein_name}
                                                                            </i>
                                                                        </small>
                                                                        <small className="d-block mb-2">
                                                                            Compound: <i style={{ textTransform: 'capitalize' }}>
                                                                                {organism.compound_name}
                                                                            </i>
                                                                        </small>
                                                                        <button
                                                                            className="btn btn-sm btn-outline-primary"
                                                                            onClick={() => window.open(`/details/${organism.id}`, '_blank')}
                                                                        >
                                                                            <i className="bi bi-box-arrow-up-right me-1"></i>
                                                                            3D Structure
                                                                        </button>
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            ) : (
                                                <div className="alert alert-info">
                                                    <i className="bi bi-info-circle me-2"></i>
                                                    No resources found for the selected criteria
                                                </div>
                                            )}

                                            {pagination.total_pages > 1 && (
                                                <div className="d-flex justify-content-center">
                                                    <Pagination className="mb-0">
                                                        <Pagination.First
                                                            onClick={() => handlePageChange(1)}
                                                            disabled={pagination.page === 1 || loading}
                                                        />
                                                        <Pagination.Prev
                                                            onClick={() => handlePageChange(pagination.page - 1)}
                                                            disabled={pagination.page === 1 || loading}
                                                        />

                                                        {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                                                            let pageNum;
                                                            if (pagination.total_pages <= 5) {
                                                                pageNum = i + 1;
                                                            } else if (pagination.page <= 3) {
                                                                pageNum = i + 1;
                                                            } else if (pagination.page >= pagination.total_pages - 2) {
                                                                pageNum = pagination.total_pages - 4 + i;
                                                            } else {
                                                                pageNum = pagination.page - 2 + i;
                                                            }

                                                            return (
                                                                <Pagination.Item
                                                                    key={pageNum}
                                                                    active={pageNum === pagination.page}
                                                                    onClick={() => handlePageChange(pageNum)}
                                                                    disabled={loading}
                                                                >
                                                                    {pageNum}
                                                                </Pagination.Item>
                                                            );
                                                        })}

                                                        <Pagination.Next
                                                            onClick={() => handlePageChange(pagination.page + 1)}
                                                            disabled={pagination.page === pagination.total_pages || loading}
                                                        />
                                                        <Pagination.Last
                                                            onClick={() => handlePageChange(pagination.total_pages)}
                                                            disabled={pagination.page === pagination.total_pages || loading}
                                                        />
                                                    </Pagination>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="modal-footer">
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => setShowModal(false)}
                                disabled={loading}
                            >
                                <i className="bi bi-x-circle me-1"></i>
                                Close
                            </button>
                            <button
                                type="button"
                                className="btn btn-primary-custom"
                                onClick={() => alert('Resources saved to your profile!')}
                                disabled={loading || organisms.length === 0}
                            >
                                <i className="bi bi-bookmark-plus me-1"></i>
                                Save Resources
                            </button>
                            <button
                                type="button"
                                className="btn btn-success"
                                onClick={() => window.print()}
                                disabled={loading || organisms.length === 0}
                            >
                                <i className="bi bi-printer me-1"></i>
                                Print Resources
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Rating Modal */}
            <Modal show={showRatingModal} onHide={() => setShowRatingModal(false)} centered>
                <Modal.Header className='bg-success text-white' closeButton>
                    <Modal.Title>
                        <i className="bi bi-star me-2"></i>
                        Rate {selectedOrganism?.organism_name}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div className="text-center mb-4">
                        <h6 className="mb-3">How would you rate this organism?</h6>
                        <StarRating
                            rating={userRating}
                            interactive={true}
                            onRatingChange={setUserRating}
                        />
                        {userRating > 0 && (
                            <p className="text-muted mt-2">
                                You selected: {userRating} star{userRating !== 1 ? 's' : ''}
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
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                        />
                    </div>

                    <div className="mb-3">
                        <label htmlFor="userEmail" className="form-label">Your Email (Optional)</label>
                        <input
                            type="email"
                            id="userEmail"
                            className="form-control"
                            placeholder="john@example.com"
                            value={userEmail}
                            onChange={(e) => setUserEmail(e.target.value)}
                        />
                    </div>

                    <div className="mb-3">
                        <label htmlFor="reviewText" className="form-label">
                            Review (Optional)
                        </label>
                        <textarea
                            id="reviewText"
                            className="form-control"
                            rows="3"
                            placeholder="Share your experience with this organism..."
                            value={userReview}
                            onChange={(e) => setUserReview(e.target.value)}
                        />
                    </div>
                </Modal.Body>
                <Modal.Footer>
                    <Button
                        variant="secondary"
                        onClick={() => setShowRatingModal(false)}
                        disabled={submittingRating}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleRatingSubmit}
                        disabled={userRating === 0 || submittingRating}
                    >
                        {submittingRating ? (
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


            {/* Reviews Modal */}
            {/* Reviews Modal */}
            <Modal show={showReviewsModal} onHide={() => setShowReviewsModal(false)} size="lg">
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
                                    {review.review && (
                                        <p className="mb-2">{review.review}</p>
                                    )}
                                    <div className="d-flex justify-content-between">
                                        <small className="text-muted">
                                            {review.reviewer_name || 'Anonymous'}
                                        </small>
                                        {review.reviewer_email && review.reviewer_email !== 'Anonymous' && (
                                            <small className="text-muted">
                                                {review.reviewer_email}
                                            </small>
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
                    <Button variant="secondary" onClick={() => setShowReviewsModal(false)}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
            <div
                className="modal-backdrop fade show"
                onClick={() => !loading && setShowModal(false)}
            ></div>
        </>
    );
};

export default ResourcesModal;