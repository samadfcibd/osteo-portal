export default function About() {
    return (

        <div className="container">
            <div className="row">
                <div className="col-12">

                    <div className="card card-custom mb-4">
                        <div className="card-body">
                            <div className="d-flex justify-content-between align-items-center mb-3">
                                <h4 className="card-title mb-0 fw-bold">
                                    <i className="bi bi-info-circle me-2 text-primary"></i>
                                    About Us
                                </h4>
                                <div className="d-flex align-items-center">
                                    {/* <div className="me-3">
                                            <span className="badge bg-primary rounded-pill">
                                                <i className="bi bi-circle-fill me-1" style={{ fontSize: '0.5rem' }}></i>
                                                Resources Available
                                            </span>
                                        </div> */}
                                    {/* <div>
                                            <span className="badge bg-danger rounded-pill">
                                                <i className="bi bi-circle-fill me-1" style={{ fontSize: '0.5rem' }}></i>
                                                Active Locations
                                            </span>
                                        </div> */}

                                </div>
                            </div>

                            <div className=" d-flex align-items-center">
                                About this project
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}