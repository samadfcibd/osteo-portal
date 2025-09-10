import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';

// material-ui
import {
    Typography,
    Button,
    Box,
    Input,
    FormControl,
    FormHelperText,
    CircularProgress,
    LinearProgress,
    TextField,
    Autocomplete
} from '@material-ui/core';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';

// project imports
import MainCard from '../../ui-component/cards/MainCard';
import configData from '../../../src/config';
import axios from 'axios';

//==============================|| Protein Compound Upload ||==============================//

const PdbUpload = () => {
    const [protein, setProtein] = useState(null);
    const [compound, setCompound] = useState(null);
    const [file, setFile] = useState(null);
    const [proteins, setProteins] = useState([]);
    const [compounds, setCompounds] = useState([]);
    const [proteinLoading, setProteinLoading] = useState(false);
    const [compoundLoading, setCompoundLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const account = useSelector((state) => state.account);
    const fileInputRef = React.useRef(null);

    // Fetch proteins from API
    useEffect(() => {
        setProteinLoading(true);
        const fetchProteins = async () => {
            try {
                const response = await axios.get(process.env.REACT_APP_BACKEND_SERVER + 'proteins');
                if (response.data.success) {
                    setProteins(response.data.data);
                } else {
                    console.error('Error fetching proteins:', response.data.message);
                    setError(response.data.message || 'Failed to load proteins');
                }
            } catch (error) {
                console.error('Error fetching proteins:', error);
                setError('Failed to load proteins');
            } finally {
                setProteinLoading(false);
            }
        };

        fetchProteins();
    }, [account.token]);

    // Fetch compounds from API
    useEffect(() => {
        setCompoundLoading(true);
        const fetchCompounds = async () => {
            try {
                const response = await axios.get(process.env.REACT_APP_BACKEND_SERVER + 'compounds');
                if (response.data.success) {
                    setCompounds(response.data.data);
                } else {
                    console.error('Error fetching compounds:', response.data.message);
                    setError(response.data.message || 'Failed to load compounds');
                }
            } catch (error) {
                console.error('Error fetching compounds:', error);
                setError('Failed to load compounds');
            } finally {
                setCompoundLoading(false);
            }
        };

        fetchCompounds();
    }, [account.token]);

    const handleProteinChange = (event, newValue) => {
        setProtein(newValue);
        setError('');
    };

    const handleCompoundChange = (event, newValue) => {
        setCompound(newValue);
        setError('');
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && (selectedFile.type === 'chemical/x-pdb' || selectedFile.name.endsWith('.pdb'))) {
            setFile(selectedFile);
            setError('');
            setSuccess('');
        } else {
            setError('Please upload a valid PDB file');
            setFile(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!protein || !compound || !file) {
            setError('Please fill all fields');
            return;
        }

        const formData = new FormData();
        formData.append('protein', protein.protein_id);
        formData.append('compound', compound.compound_id);
        formData.append('file', file);
        formData.append('token', `${account.token}`);

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await axios.post(
                `${configData.API_SERVER}protein-compound-upload`,
                formData,
                {
                    headers: {
                        Authorization: `${account.token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            setSuccess(response.data.message || 'Data uploaded successfully!');
            setProtein(null);
            setCompound(null);
            setFile(null);

            // Clear the file input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }

        } catch (err) {
            console.error('Upload error:', err);

            const errorMessage = err.response?.data?.message
                || err.response?.data?.error
                || err.message
                || 'An error occurred during upload';

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <MainCard title="Protein-Compound Upload">
            <Typography variant="body2" paragraph>
                Please select a protein and compound, then upload a PDB file for analysis.
            </Typography>

            <form onSubmit={handleSubmit}>
                {/* Protein Search Select Field */}
                <Box mt={2} mb={3}>
                    <FormControl fullWidth error={Boolean(error && !protein)}>
                        <Autocomplete
                            id="protein-search"
                            options={proteins}
                            getOptionLabel={(option) => option.protein_name}
                            value={protein}
                            onChange={handleProteinChange}
                            loading={proteinLoading}
                            disabled={loading}
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    label="Search and select protein"
                                    variant="outlined"
                                    InputProps={{
                                        ...params.InputProps,
                                        endAdornment: (
                                            <React.Fragment>
                                                {proteinLoading ? <CircularProgress color="inherit" size={20} /> : null}
                                                {params.InputProps.endAdornment}
                                            </React.Fragment>
                                        ),
                                    }}
                                />
                            )}
                            noOptionsText={proteinLoading ? "Loading proteins..." : "No proteins found"}
                        />
                    </FormControl>
                </Box>

                {/* Compound Search Select Field */}
                <Box mb={3}>
                    <FormControl fullWidth error={Boolean(error && !compound)}>
                        <Autocomplete
                            id="compound-search"
                            options={compounds}
                            getOptionLabel={(option) => option.compound_name}
                            value={compound}
                            onChange={handleCompoundChange}
                            loading={compoundLoading}
                            disabled={loading}
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    label="Search and select compound"
                                    variant="outlined"
                                    InputProps={{
                                        ...params.InputProps,
                                        endAdornment: (
                                            <React.Fragment>
                                                {compoundLoading ? <CircularProgress color="inherit" size={20} /> : null}
                                                {params.InputProps.endAdornment}
                                            </React.Fragment>
                                        ),
                                    }}
                                />
                            )}
                            noOptionsText={compoundLoading ? "Loading compounds..." : "No compounds found"}
                        />
                    </FormControl>
                </Box>

                {/* File Input */}
                <Box mb={3}>
                    <FormControl fullWidth error={Boolean(error)}>
                        <Input
                            id="file-upload"
                            type="file"
                            inputProps={{ accept: '.pdb' }}
                            onChange={handleFileChange}
                            disabled={loading}
                            inputRef={fileInputRef}
                        />
                        {error && <FormHelperText error>{error}</FormHelperText>}
                        {success && (
                            <Box display="flex" alignItems="center" mt={1}>
                                <CheckCircleIcon style={{ color: 'green', marginRight: 8 }} />
                                <FormHelperText style={{ color: 'green' }}>{success}</FormHelperText>
                            </Box>
                        )}
                    </FormControl>
                </Box>

                {loading && (
                    <Box mb={2}>
                        <LinearProgress />
                        <Typography variant="body2" color="textSecondary" align="center" style={{ marginTop: 8 }}>
                            Processing your data, please wait...
                        </Typography>
                    </Box>
                )}

                <Box display="flex" alignItems="center" gap={2}>
                    <Button
                        variant="contained"
                        color="primary"
                        type="submit"
                        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                        disabled={!protein || !compound || !file || loading}
                    >
                        {loading ? 'Processing...' : 'Upload Data'}
                    </Button>
                </Box>
            </form>
        </MainCard>
    );
};

export default PdbUpload;