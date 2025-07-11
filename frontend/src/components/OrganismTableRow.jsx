import StarRating from "./StarRating";

const OrganismTableRow = ({ organism, onRate, onViewReviews }) => (
    <tr key={organism.data_id}>
        <td>
            <div className="d-flex align-items-center">
                <div>
                    <h6 className="mb-0">{organism.organism_name}</h6>
                    <small className={organism.gbifFound ? 'text-success' : 'text-danger'}>
                        {organism.gbifFound ? '✅ Found in your country' : '❌ Not Found in your country'}
                    </small>
                </div>
            </div>
        </td>
        <td style={{ maxWidth: "200px" }}>
            <div className="d-flex flex-wrap gap-1">
                {/* <span className="badge bg-light text-dark">Turmeric</span>
                <span className="badge bg-light text-dark">Fish Oil</span>
                <span className="badge bg-light text-dark">Leafy Greens</span> */}

                {organism.vernacularNames?.length > 0 ? (
                    organism.vernacularNames.map((name, index) => (
                        <span key={index} className="badge bg-success text-light" style={{whiteSpace: "wrap"}}>
                            {name}
                        </span>
                    ))
                ) : (
                    <span className="badge bg-light text-dark">No common names found</span>
                )}
            </div>
        </td>
        <td>
            {/* <StarRating rating={organism.rating} />
            <div className="d-flex gap-2 mt-1">
                <button
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => onRate(organism)}
                >
                    <i className="bi bi-star me-1"></i>Rate
                </button>
                <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => onViewReviews(organism.organism_id)}
                >
                    <i className="bi bi-chat-square-text me-1"></i>Reviews
                </button>
            </div> */}

            <span className="text-muted">No ratings yet</span>
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
                <i className="bi bi-box-arrow-up-right me-1"></i>3D Structure
            </button>
        </td>
    </tr>
);

export default OrganismTableRow;