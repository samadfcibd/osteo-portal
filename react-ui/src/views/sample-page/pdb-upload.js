import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';

// material-ui
import {
    Typography,
    Button,
    Box,
    Input,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormHelperText,
    CircularProgress,
    LinearProgress
} from '@material-ui/core';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';

// project imports
import MainCard from '../../ui-component/cards/MainCard';

import configData from '../../../src/config';
import axios from 'axios';

//==============================|| Protein Compound Upload ||==============================//

const PdbUpload = () => {
    const [protein, setProtein] = useState('');
    const [compound, setCompound] = useState('');
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
            } finally {
                setProteinLoading(false);
            }
        };

        fetchProteins();
    }, [account.token]);

    // Fetch compounds from API
    useEffect(() => {

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
            } finally {
                setCompoundLoading(false);
            }
        };

        fetchCompounds();
    }, [account.token]);

    const handleProteinChange = (e) => {
        setProtein(e.target.value);
        setError('');
    };

    const handleCompoundChange = (e) => {
        setCompound(e.target.value);
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
        formData.append('protein', protein);
        formData.append('compound', compound);
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
            setProtein('');
            setCompound('');
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
                {/* Protein Select Field */}
                <Box mt={2} mb={3}>
                    <FormControl fullWidth error={Boolean(error && !protein)}>
                        <InputLabel id="protein-select-label">Protein</InputLabel>
                        <Select
                            labelId="protein-select-label"
                            id="protein-select"
                            value={protein}
                            onChange={handleProteinChange}
                            disabled={proteinLoading || loading}
                        >
                            {proteins.map((protein) => (
                                <MenuItem key={protein.protein_id} value={protein.protein_id}>
                                    {protein.protein_name}
                                </MenuItem>
                            ))}
                        </Select>
                        {proteinLoading && <FormHelperText>Loading proteins...</FormHelperText>}
                    </FormControl>
                </Box>

                {/* Compound Select Field */}
                <Box mb={3}>
                    <FormControl fullWidth error={Boolean(error && !compound)}>
                        <InputLabel id="compound-select-label">Compound</InputLabel>
                        <Select
                            labelId="compound-select-label"
                            id="compound-select"
                            value={compound}
                            onChange={handleCompoundChange}
                            disabled={compoundLoading || loading}
                        >
                            {compounds.map((compound) => (
                                <MenuItem key={compound.compound_id} value={compound.compound_id}>
                                    {compound.compound_name}
                                </MenuItem>
                            ))}
                        </Select>
                        {compoundLoading && <FormHelperText>Loading compounds...</FormHelperText>}
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