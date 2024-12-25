import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';
import './CDforMyCourses.css';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  const storedUser = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/accounts/api/course/${id}/`)
      .then((response) => {
        setCourse(response.data);
        setLoading(false);
      })
      .catch((error) => console.error('Error fetching course details:', error));
  }, [id]);

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="my-course-detail">
      <Navbar />
      <div className="my-course-content">
        <h1>{course.title}</h1>
        <p>{course.description}</p>
        <h2>Содержание курса:</h2>
        <div className="my-course-content-details">{course.content}</div>
            {storedUser?.is_superuser && (
                <button className="my-course-button" onClick={() => navigate(`/courses/${id}/add-form`)}>Добавить форму</button>
            )}
            <button className="my-course-button" onClick={() => navigate(`/courses/${id}/quiz`)}>Пройти тест</button>
      </div>
      <Footer />
    </div>
  );
};

export default CourseDetail;
