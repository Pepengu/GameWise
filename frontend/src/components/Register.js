import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        profile_photo: null,
    });
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        if (e.target.name === "profile_photo") {
            setFormData({ ...formData, profile_photo: e.target.files[0] });
        } else {
            setFormData({ ...formData, [e.target.name]: e.target.value });
        }
    };

    const handleFileChange = (e) => {
        setFormData({ ...formData, profile_photo: e.target.files[0] });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const formDataObj = new FormData();
        formDataObj.append("username", formData.username);
        formDataObj.append("email", formData.email);
        formDataObj.append("password", formData.password);
        formDataObj.append("password2", formData.password2);
        formDataObj.append("profile_photo", formData.profile_photo);

        try {
            const response = await axios.post('http://127.0.0.1:8000/accounts/register/', formDataObj, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(response.data.message);
            if (response.status === 201) {
                navigate('/home');
            }
        } catch (error) {
            setMessage(error.response?.data?.error || "An error occurred");
        }
    };

    return (
        <div className="form-container">
            <h1>Register</h1>
            <form onSubmit={handleSubmit}>
                <input type="text" name="username" placeholder="Username" onChange={handleChange} />
                <input type="email" name="email" placeholder="Email" onChange={handleChange} />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} />
                <input type="password" name="password2" placeholder="Confirm Password" onChange={handleChange} />
                <input type="file" name="profile_photo" onChange={handleFileChange} />
                <button type="submit">Register</button>
            </form>
            <p>{message}</p>
            <div className="switch-container">
                <p>
                    Already have an account?
                    <span
                        style={{ color: "blue", cursor: "pointer", marginLeft: '5px' }}
                        onClick={() => navigate('/login')}
                    >
                        Login
                    </span>
                </p>
            </div>
        </div>
    );
};

export default Register;

