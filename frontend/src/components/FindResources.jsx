import { useState, useEffect } from 'react'
import WorldMap from './WorldMap'
import ResourcesModal from './ResourcesModal'
import * as am5geodata_data_countries2 from "@amcharts/amcharts5-geodata/data/countries2";
import SelectSearch from 'react-select';
import axios from 'axios';




const FindResources = () => {

    const [stages, setStage] = useState([]);
    const [selectedStage, setSelectedStage] = useState('');
    const [selectedCountry, setSelectedCountry] = useState('');
    const [showSearchBtn, setShowSearchBtn] = useState(false);
    const [showModal, setShowModal] = useState(false);


    // Handle country selection
    const handleCountryChange = (selectedOption) => {

        const countryCode = selectedOption?.value || null;

        setSelectedCountry(countryCode);

        if (selectedOption?.value) {
            // Handle country selection
            console.log("Selected country:", selectedOption.value);
        } else {
            // Handle clear/unselect
            console.log("Country selection cleared");

        }
    };

    // This will be called when a country is clicked on the map
    const handleMapCountrySelect = (countryCode) => {
        setSelectedCountry(countryCode);
    };


    // Get the actual data object (default export contains the data)
    const geoData = am5geodata_data_countries2.default;

    // Extract country list
    const countryList = Object.keys(geoData)
        .filter(key => key.length === 2) // Only country codes (2 letters)
        .map(code => ({
            id: code,
            code: code,
            name: geoData[code].country,
            continent: geoData[code].continent,
            continent_code: geoData[code].continent_code
        }));

    const countries = countryList.map(country => ({
        value: country.code || country.id,  // Use whichever field exists
        label: country.name || country.country,  // Different possible name fields
    }));


    // Fetch clinical stages only once on component mount
    useEffect(() => {

        const fetchClinicalStages = async () => {
            try {
                const response = await axios.get(import.meta.env.VITE_API_URL + '/api/clinical-stages');
                if (response.data.success) {
                    setStage(response.data.data);
                } else {
                    // Alert error
                }

            } catch (error) {
                console.error('Error fetching stages:', error);
            }
        };

        fetchClinicalStages();
    }, []); // Empty dependency array means it runs only once

    // Check if modal should open when country changes
    useEffect(() => {

        if (selectedStage && selectedCountry) {
            setShowSearchBtn(true);
            // setShowModal(true);
        } else {
            setShowSearchBtn(false);
        }
    }, [selectedStage, selectedCountry]);

    return (
        <>
            <div className="container" style={{ marginTop: '80px' }}>
                <div className="row">
                    <div className="col-12">
                        {/* Filter Section */}
                        <div className="card card-custom mb-4">
                            <div className="card-body">
                                <div className="row align-items-center">
                                    <div className="col-lg-6 mb-3 mb-lg-0">
                                        <h4 className="card-title mb-2 fw-bold">
                                            <i className="bi bi-funnel me-2 text-primary"></i>
                                            Find Resources by Location & Stage
                                        </h4>
                                        <p className="card-text text-muted mb-0">
                                            Select your osteoarthritis stage and country to discover relevant natural treatment options
                                        </p>
                                    </div>
                                    <div className="col-lg-6">
                                        <div className="row g-3">
                                            <div className="col-md-6">
                                                <label className="form-label fw-semibold">
                                                    <i className="bi bi-clipboard-check me-1"></i>
                                                    Stage
                                                </label>
                                                <select
                                                    className="form-select form-select-custom"
                                                    value={selectedStage}
                                                    onChange={(e) => setSelectedStage(e.target.value)}
                                                >
                                                    {stages.map((stage) => (
                                                        <option key={stage.stage_id} value={stage.stage_id}>
                                                            {stage.stage_name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label fw-semibold">
                                                    <i className="bi bi-globe me-1"></i>
                                                    Country
                                                </label>

                                                <SelectSearch
                                                    options={countries}
                                                    isClearable={true}
                                                    value={countries.find(c => c.value === selectedCountry) || null}
                                                    onChange={handleCountryChange}
                                                    placeholder="Select a country"
                                                    classNamePrefix="react-select"
                                                    menuPortalTarget={document.body}
                                                    styles={{
                                                        menuPortal: base => ({ ...base, zIndex: 9999 })
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* World Map Section */}
                        <div className="card card-custom mb-4">
                            <div className="card-body">
                                <div className="d-flex justify-content-between align-items-center mb-3">
                                    <h4 className="card-title mb-0 fw-bold">
                                        <i className="bi bi-map me-2 text-primary"></i>
                                        Global Resource Map
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
                                        <div className={` ${showSearchBtn ? 'show' : ''}`}
                                            style={{ display: showSearchBtn ? 'block' : 'none' }}>
                                            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                                                <i className="bi bi-search me-2"></i>
                                                Search Resources
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <div className="map-container d-flex align-items-center justify-content-center">
                                    <div className="position-relative w-100">
                                        <WorldMap country={selectedCountry}
                                            onCountrySelect={handleMapCountrySelect}  // Pass the callback
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Selected Filters Display */}
                        {/* {(selectedStage || selectedCountry) && (
              <div className="alert alert-custom mb-4">
                <h5 className="alert-heading fw-bold">
                  <i className="bi bi-check-circle me-2"></i>
                  Current Selection
                </h5>
                <div className="d-flex flex-wrap gap-2 mb-0">
                  {selectedStage && (
                    <span className="badge-custom me-2">
                      <i className="bi bi-clipboard-check me-1"></i>
                      Stage: {stages.find(s => s.value === selectedStage)?.label}
                    </span>
                  )}
                  {selectedCountry && (
                    <span className="badge-custom">
                      <i className="bi bi-globe me-1"></i>
                      Country: {countries.find(c => c.value === selectedCountry)?.label}
                    </span>
                  )}
                </div>
              </div>
            )} */}

                        {/* Action Buttons */}
                        {/* <div className="text-center mb-5">
                            <button className="btn btn-primary-custom btn-lg me-3">
                                <i className="bi bi-search me-2"></i>
                                Search Resources
                            </button>
                            <button className="btn btn-outline-primary btn-lg">
                                <i className="bi bi-filter me-2"></i>
                                Advanced Filters
                            </button>
                        </div> */}
                    </div>
                </div>
            </div>


            <ResourcesModal
                showModal={showModal}
                setShowModal={setShowModal}
                selectedStage={selectedStage}
                selectedCountry={selectedCountry}
                stages={stages}
                countries={countries}
            />
        </>
    )
}
export default FindResources;