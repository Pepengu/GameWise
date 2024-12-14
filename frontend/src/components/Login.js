import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/accounts/login/', formData);
            setMessage(response.data.message);
            setTimeout(() => navigate('/home'), 2000);
        } catch (error) {
            setMessage(error.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="form-container">
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <input type="text" name="username" placeholder="Username" onChange={handleChange} />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} />
                <button type="submit">Login</button>
            </form>
            <p>{message}</p>
            <div className="switch-container">
                <p>
                    Don't have an account?
                    <span
                        style={{ color: "blue", cursor: "pointer", marginLeft: '5px' }}
                        onClick={() => navigate('/register')}
                    >
                        Register
                    </span>
                </p>
            </div>
        </div>
    );
};

export default Login;

