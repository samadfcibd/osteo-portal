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
        const account = useSelector((state) => state.account);
        const fileInputRef = React.useRef(null);

        const handleFileChange = (e) => {
            const selectedFile = e.target.files[0];
            if (selectedFile && selectedFile.type === 'text/csv') {
                setFile(selectedFile);
                setError('');
                setSuccess('');
            } else {
                setError('Please upload a valid CSV file');
                setFile(null);
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
            <MainCard title="Organism Upload">
                <Typography variant="body2" paragraph>
                    Please upload a CSV file containing organism data. The file should follow the specified format.
                </Typography>

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

                    <Box display="flex" alignItems="center" gap={2}>
                        <Button
                            variant="contained"
                            color="primary"
                            type="submit"
                            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                            disabled={!file || loading}
                        >
                            {loading ? 'Processing...' : 'Upload CSV'}
                        </Button>
                    </Box>
                </form>
            </MainCard>
        );
    };

    export default OrganismUpload;