import React, { useState } from 'react';
import axios from 'axios';

type ApplyLeaveProps = {};

const ApplyLeave: React.FC<ApplyLeaveProps> = () => {
    const [formData, setFormData] = useState({
        category: 'CL' as 'CL' | 'RH' | 'SCL' | 'EL' | 'COL' | 'VL',
        start_date: '',
        end_date: '',
        purpose: '',
        is_station_leave: false,
        station_address: ''
    });

    const [error, setError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type, checked } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (new Date(formData.start_date) < new Date(formData.end_date)) {
            try {
                const response = await axios.post('/api/elm/apply/', formData);
                alert('Leave application submitted successfully!');
            } catch (error) {
                setError('Error submitting leave application.');
            }
        } else {
            setError('Start date must be before or equal to end date.');
        }
    };

    return (
        <div className="fusion-card p-6">
            <h2 className="text-xl font-bold mb-4">Apply for Leave (ELM)</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="category">Category:</label>
                    <select
                        id="category"
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                        required
                    >
                        <option value="CL">Casual Leave (CL)</option>
                        <option value="RH">Restricted Holiday (RH)</option>
                        <option value="SCL">Special Casual Leave (SCL)</option>
                        <option value="EL">Earned Leave (EL)</option>
                        <option value="COL">Commuted Leave (COL)</option>
                        <option value="VL">Vacation Leave (VL)</option>
                    </select>
                </div>

                <div>
                    <label htmlFor="start_date">Start Date:</label>
                    <input
                        id="start_date"
                        name="start_date"
                        type="date"
                        value={formData.start_date}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="end_date">End Date:</label>
                    <input
                        id="end_date"
                        name="end_date"
                        type="date"
                        value={formData.end_date}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="purpose">Purpose:</label>
                    <textarea
                        id="purpose"
                        name="purpose"
                        value={formData.purpose}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="is_station_leave">Station Leave:</label>
                    <input
                        id="is_station_leave"
                        name="is_station_leave"
                        type="checkbox"
                        checked={formData.is_station_leave}
                        onChange={handleChange}
                    />
                </div>

                <div>
                    {formData.is_station_leave && (
                        <div>
                            <label htmlFor="station_address">Station Address:</label>
                            <input
                                id="station_address"
                                name="station_address"
                                type="text"
                                value={formData.station_address}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    )}
                </div>

                {error && <p className="text-red-500">{error}</p>}

                <button type="submit" className="fusion-button-primary">Submit Application</button>
            </form>
        </div>
    );
};

export default ApplyLeave;