import React, { useState } from 'react';
import { Box, Typography, Slider, Button, Radio, RadioGroup, FormControl, FormControlLabel } from '@mui/material';

const Sidebar = ({ onUpdate }) => {
  // States to manage Total Layers and Resource values
  const [totalLayers, setTotalLayers] = useState(1);
  const [resource, setResource] = useState(100);
  const [modelType, setModelType] = useState('prob'); // Default to probabilistic model

  // Handlers
  const handleTotalLayersChange = (event, newValue) => {
    setTotalLayers(newValue);
  };

  const handleResourceChange = (event, newValue) => {
    setResource(newValue);
  };

  const handleModelTypeChange = (event) => {
    setModelType(event.target.value);
  };

  const handleSubmit = () => {
    if (onUpdate) {
      onUpdate({ totalLayers, resource, modelType });
    }
  };

  return (
    <Box
      sx={{
        padding: 3,
        width: '100%', // Use 100% of the parent width
        maxWidth: '300px', // Limit the max width to 300px
        borderRight: '1px solid #ddd',
        boxSizing: 'border-box', // Prevent extra spacing due to padding
      }}
    >
      <Typography variant="h6" gutterBottom>
        Configuration
      </Typography>

      {/* Model Type Selection */}
      <FormControl component="fieldset" sx={{ marginBottom: 3 }}>
        <Typography variant="subtitle1">Model Type:</Typography>
        <RadioGroup value={modelType} onChange={handleModelTypeChange}>
          <FormControlLabel value="prob" control={<Radio />} label="Probabilistic Model" />
        </RadioGroup>
      </FormControl>

      {/* Total Layers Slider */}
      <Box sx={{ marginBottom: 3 }}>
        <Typography variant="subtitle1">Total Layers:</Typography>
        <Slider
          value={totalLayers}
          onChange={handleTotalLayersChange}
          min={1}
          max={5}
          step={1}
          valueLabelDisplay="auto"
        />
        <Typography variant="body2">Selected: {totalLayers}</Typography>
      </Box>

      {/* Resource Slider */}
      <Box sx={{ marginBottom: 3 }}>
        <Typography variant="subtitle1">Resource:</Typography>
        <Slider
          value={resource}
          onChange={handleResourceChange}
          min={0}
          max={500}
          step={5}
          valueLabelDisplay="auto"
        />
        <Typography variant="body2">Selected: {resource}</Typography>
      </Box>

      {/* Submit Button */}
      <Button variant="contained" color="primary" onClick={handleSubmit} fullWidth>
        Update
      </Button>
    </Box>
  );
};

export default Sidebar;
