import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Spinner, Pagination } from 'react-bootstrap';
import OrganismTableRow from './OrganismTableRow';
import RatingModal from './RatingModal';
import ReviewsModal from './ReviewsModal';

// Constants
const INITIAL_PAGINATION = {
    page: 1,
    per_page: 10,
    total: 0,
    total_pages: 0
};

const INITIAL_RATING_STATE = {
    userRating: 0,
    userReview: '',
    userName: '',
    userEmail: ''
};

// Custom hooks
const useApi = () => {
    const baseURL = import.meta.env.VITE_API_URL;

    return useMemo(() => ({
        fetchOrganisms: (stage, page, perPage) =>
            axios.get(`${baseURL}/api/organisms`, {
                params: { stage, page, per_page: perPage }
            }),

        fetchReviews: (organismId) =>
            axios.get(`${baseURL}/api/organisms/${organismId}/reviews`),

        fetchRating: (organismId) =>
            axios.get(`${baseURL}/api/organisms/${organismId}/rating`),

        submitRating: (organismId, data) =>
            axios.post(`${baseURL}/api/organisms/${organismId}/rating`, data)
    }), [baseURL]);
};

const useGbifEnrichment = (selectedCountry) => {
    const enrichWithGbifData = useCallback(async (organismsList) => {
        const enriched = await Promise.allSettled(
            organismsList.map(async (org) => {
                try {
                    const [occurrenceRes, imageRes] = await Promise.all([
                        axios.get("https://api.gbif.org/v1/occurrence/search", {
                            params: {
                                scientificName: org.organism_name,
                                country: selectedCountry,
                                limit: 0
                            }
                        }),
                        axios.get("https://api.gbif.org/v1/occurrence/search", {
                            params: {
                                scientificName: org.organism_name,
                                mediaType: "StillImage",
                                limit: 2,
                                hasCoordinate: true,
                                hasGeospatialIssue: false
                            }
                        })
                    ]);

                    const found = occurrenceRes.data.count > 0;
                    const images = imageRes.data.results.flatMap(r => r.media?.map(m => m.identifier) || []);
                    const kingdom = imageRes?.data?.results?.[0]?.kingdom ?? org.organism_type;

                    return {
                        ...org,
                        gbifKingdom: kingdom,
                        gbifFound: found,
                        gbifImages: images
                    };
                } catch (error) {
                    console.warn(`GBIF error for ${org.organism_name}`, error);
                    return {
                        ...org,
                        gbifKingdom: org.organism_type,
                        gbifFound: false,
                        gbifImages: []
                    };
                }
            })
        );

        return enriched.map(result =>
            result.status === 'fulfilled' ? result.value : result.reason
        );
    }, [selectedCountry]);

    return { enrichWithGbifData };
};

// Main Component
const ResourcesModal = ({ showModal, setShowModal, selectedStage, selectedCountry, stages, countries }) => {
    // State management
    const [organisms, setOrganisms] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState(INITIAL_PAGINATION);

    // Modal states
    const [showRatingModal, setShowRatingModal] = useState(false);
    const [showReviewsModal, setShowReviewsModal] = useState(false);
    const [selectedOrganism, setSelectedOrganism] = useState(null);
    const [ratingState, setRatingState] = useState(INITIAL_RATING_STATE);
    const [reviews, setReviews] = useState([]);
    const [submittingRating, setSubmittingRating] = useState(false);

    // Custom hooks
    const api = useApi();
    const { enrichWithGbifData } = useGbifEnrichment(selectedCountry);

    // Handlers
    const fetchOrganismList = useCallback(async (page = 1) => {
        if (!selectedStage) return;

        setLoading(true);
        setError(null);

        try {
            const response = await api.fetchOrganisms(selectedStage, page, pagination.per_page);

            if (response.data.success) {
                const enrichedOrganisms = await enrichWithGbifData(response.data.data);
                setOrganisms(enrichedOrganisms);
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
    }, [selectedStage, pagination.per_page, api, enrichWithGbifData]);

    const handleRateOrganism = useCallback((organism) => {
        setSelectedOrganism(organism);
        setRatingState(INITIAL_RATING_STATE);
        setShowRatingModal(true);
    }, []);

    const handleViewReviews = useCallback(async (organismId) => {
        try {
            const response = await api.fetchReviews(organismId);
            setReviews(response.data?.data?.reviews || []);
            setShowReviewsModal(true);
        } catch (error) {
            console.error('Error fetching reviews:', error);
            setReviews([]);
            alert('Failed to load reviews');
        }
    }, [api]);

    const handleRatingSubmit = useCallback(async () => {
        if (!selectedOrganism || ratingState.userRating === 0) {
            alert('Please select a rating before submitting.');
            return;
        }

        setSubmittingRating(true);
        try {
            await api.submitRating(selectedOrganism.organism_id, {
                rating: ratingState.userRating,
                review: ratingState.userReview,
                user_name: ratingState.userName,
                user_email: ratingState.userEmail
            });

            setRatingState(INITIAL_RATING_STATE);
            await fetchOrganismList(pagination.page);
            setShowRatingModal(false);
            alert('Rating submitted successfully!');
        } catch (error) {
            alert('Failed to submit rating. Please try again.');
        } finally {
            setSubmittingRating(false);
        }
    }, [selectedOrganism, ratingState, api, fetchOrganismList, pagination.page]);

    const handlePageChange = useCallback((page) => {
        setPagination(prev => ({ ...prev, page }));
        fetchOrganismList(page);
    }, [fetchOrganismList]);

    // Effects
    useEffect(() => {
        if (selectedStage && showModal) {
            fetchOrganismList();
        }
    }, [selectedStage, showModal, fetchOrganismList]);

    // Computed values
    const selectedStageInfo = useMemo(() =>
        stages.find(s => s.stage_id == selectedStage), [stages, selectedStage]
    );

    const selectedCountryInfo = useMemo(() =>
        countries.find(c => c.value === selectedCountry), [countries, selectedCountry]
    );

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
                            />
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
                                                        {selectedStageInfo?.stage_name}
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
                                                        {selectedCountryInfo?.label}
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
                                                                <OrganismTableRow
                                                                    key={organism.data_id}
                                                                    organism={organism}
                                                                    onRate={handleRateOrganism}
                                                                    onViewReviews={handleViewReviews}
                                                                />
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
                                <i className="bi bi-x-circle me-1"></i>Close
                            </button>
                            <button
                                type="button"
                                className="btn btn-primary-custom"
                                onClick={() => alert('Resources saved to your profile!')}
                                disabled={loading || organisms.length === 0}
                            >
                                <i className="bi bi-bookmark-plus me-1"></i>Save Resources
                            </button>
                            <button
                                type="button"
                                className="btn btn-success"
                                onClick={() => window.print()}
                                disabled={loading || organisms.length === 0}
                            >
                                <i className="bi bi-printer me-1"></i>Print Resources
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <RatingModal
                show={showRatingModal}
                onHide={() => setShowRatingModal(false)}
                organism={selectedOrganism}
                ratingState={ratingState}
                onRatingStateChange={setRatingState}
                onSubmit={handleRatingSubmit}
                isSubmitting={submittingRating}
            />

            <ReviewsModal
                show={showReviewsModal}
                onHide={() => setShowReviewsModal(false)}
                reviews={reviews}
            />

            <div
                className="modal-backdrop fade show"
                onClick={() => !loading && setShowModal(false)}
            />
        </>
    );
};

export default ResourcesModal;