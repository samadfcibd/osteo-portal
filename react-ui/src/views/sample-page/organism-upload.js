import React, { useState } from 'react';
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
    LinearProgress
} from '@material-ui/core';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import GetAppIcon from '@material-ui/icons/GetApp';

// project imports
import MainCard from '../../ui-component/cards/MainCard';
import configData from '../../../src/config';
import axios from 'axios';

//==============================|| Organism Upload ||==============================//

const OrganismUpload = () => {
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const [templateLoading, setTemplateLoading] = useState(false);
    const account = useSelector((state) => state.account);
    const fileInputRef = React.useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv'))) {
            setFile(selectedFile);
            setError('');
            setSuccess('');
        } else {
            setError('Please upload a valid CSV file');
            setFile(null);
        }
    };

    const handleDownloadTemplate = async () => {
        setTemplateLoading(true);
        try {
            // Fetch the template file from public directory
            const response = await fetch(`${process.env.REACT_APP_PUBLIC_URL}/templates/example_template.csv`);
            console.log(`${process.env.REACT_APP_PUBLIC_URL}/templates/example_template.csv`)
            if (!response.ok) {
                throw new Error('Failed to download template');
            }
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            // Create a temporary anchor element to trigger download
            const a = document.createElement('a');
            a.href = url;
            a.download = 'example_template.csv';
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (err) {
            console.error('Error downloading template:', err);
            setError('Failed to download template. Please try again.');
        } finally {
            setTemplateLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) {
            setError('Please select a CSV file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('token', `${account.token}`);

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            console.log('Using token:', account.token);

            const response = await axios.post(
                `${configData.API_SERVER}csv-import/import-research-data`,
                formData,
                {
                    headers: {
                        Authorization: `${account.token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            setSuccess(response.data.message || 'File uploaded and processed successfully!');
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
        <MainCard title="Molecular Target Data Upload">
            <Typography variant="body2" paragraph>
                Upload a CSV file containing molecular target data. Download the template below to ensure proper formatting.
            </Typography>

            {/* Template download section */}
            <Box mb={3} p={2} bgcolor="#f5f5f5" borderRadius={4}>
                <Typography variant="h6" gutterBottom>
                    Download CSV Template
                </Typography>
                <Typography variant="body2" paragraph>
                    Use this template to ensure your data is formatted correctly. The template matches the structure of your sample file.
                </Typography>
                <Button
                    variant="outlined"
                    color="primary"
                    startIcon={templateLoading ? <CircularProgress size={20} color="inherit" /> : <GetAppIcon />}
                    onClick={handleDownloadTemplate}
                    disabled={loading || templateLoading}
                >
                    {templateLoading ? 'Downloading...' : 'Download Template'}
                </Button>
            </Box>

            {/* CSV format instructions */}
            <Box mb={3}>
                <Typography variant="h6" gutterBottom>
                    CSV Format Requirements
                </Typography>
                <Typography variant="body2" component="div">
                    <ul>
                        <li>File must be in CSV format with UTF-8 encoding</li>
                        <li>First row must contain column headers exactly as shown in the template</li>
                        <li>Required columns: Target, cell_type, clinical_stage, compound_name, iupac_name, X.CDOCKER_ENERGY, organisms, Processesd</li>
                        <li>Multiple values in cell_type and clinical_stage should be comma-separated</li>
                        <li>Multiple organisms should be pipe-separated (|)</li>
                        <li>Processesd column should contain TRUE or FALSE values</li>
                        <li>Special characters in iupac_name should use the ~{ } notation as shown in the template</li>
                    </ul>
                </Typography>
            </Box>

            <form onSubmit={handleSubmit}>
                <Box mt={2} mb={3}>
                    <FormControl fullWidth error={Boolean(error)}>
                        <Input
                            id="file-upload"
                            type="file"
                            inputProps={{ accept: '.csv' }}
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
                            Processing your file, please wait...
                        </Typography>
                    </Box>
                )}

                <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                    <Button
                        variant="contained"
                        color="primary"
                        type="submit"
                        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                        disabled={!file || loading}
                    >
                        {loading ? 'Processing...' : 'Upload CSV'}
                    </Button>

                    {file && (
                        <Typography variant="body2" color="textSecondary">
                            Selected file: {file.name}
                        </Typography>
                    )}
                </Box>
            </form>
        </MainCard>
    );
};

export default OrganismUpload;