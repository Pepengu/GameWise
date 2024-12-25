import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';
import './CourseDetail.css';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/accounts/api/course/${id}/`)
      .then((response) => {
        setCourse(response.data);
        setLoading(false);
      })
      .catch((error) => console.error('Error fetching course details:', error));

    const storedUser = JSON.parse(localStorage.getItem('user'));
    setUser(storedUser);
  }, [id]);

  const handleEnroll = async () => {
    if (!user || !user.id) {
      alert('Вы должны быть авторизованы, чтобы записаться на курс.');
      navigate('/login');
      return;
    }

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/accounts/api/courses/${id}/enroll/`,
        { user_id: user.id },
        { headers: { 'Content-Type': 'application/json' } }
      );
      alert(response.data.message);
    } catch (error) {
      alert(
        error.response?.data?.error ||
          'Ошибка при записи на курс. Попробуйте позже.'
      );
      console.error('Enroll error:', error);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="course-detail">
      <Navbar />
      <div className="course-content">
        <h1>{course.title}</h1>
        <p>{course.description}</p>
        <h2>Содержание курса:</h2>
        <div className="course-content-details">{course.content}</div>
        <button className="in-course-button" onClick={handleEnroll}>
          Записаться на курс
        </button>
      </div>
      <Footer />
    </div>
  );
};

export default CourseDetail;
