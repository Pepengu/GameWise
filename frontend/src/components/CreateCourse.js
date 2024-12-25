import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';
import './CreateCourse.css';

const CreateCourse = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [content, setContent] = useState('');
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (!storedUser || !storedUser.is_superuser) {
      setError('Доступ разрешен только суперпользователям.');
      navigate('/home');
    } else {
      setUser(storedUser);
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/accounts/api/courses/create/',
        {
          title,
          description,
          tags,
          content,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      alert(response.data.message);
      navigate('/catalog');
    } catch (error) {
      alert(
        error.response?.data?.error || 'Ошибка при создании курса. Попробуйте позже.'
      );
    }
  };

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div className="create-course">
      <Navbar />
      <div className='create-course-content'>
      <div className="cc-form-container">
        <h1>Создать новый курс</h1>
        <form onSubmit={handleSubmit}>
          <div className="cc-form-group">
            <label htmlFor="title">Название курса</label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="cc-form-group">
            <label htmlFor="description">Описание</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>
          <div className="cc-form-group">
            <label htmlFor="tags">Теги (через запятую)</label>
            <input
              type="text"
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>
          <div className="cc-form-group">
            <label htmlFor="content">Контент</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="cc-submit-button">
            Создать курс
          </button>
        </form>
      </div>
      </div>
      <Footer />
    </div>
  );
};

export default CreateCourse;
