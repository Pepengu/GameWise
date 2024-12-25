import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';
import { useNavigate } from 'react-router-dom';
import './MyCourses.css';
import './Catalog.css';
import math from './math.jpg';

const MyCourses = () => {
  const [, setUser] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserCourses = async () => {
      try {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
          throw new Error('User data not found in localStorage.');
        }

        const userData = JSON.parse(storedUser);
        if (!userData || !userData.id) {
          throw new Error('Invalid user data.');
        }

        setUser(userData);

        const coursesResponse = await axios.get(`http://127.0.0.1:8000/accounts/api/user/${userData.id}/courses/`);
        setEnrollments(coursesResponse.data.courses);
      } catch (err) {
        setError('Не удалось загрузить курсы.');
        console.error('Error fetching user courses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserCourses();
  }, []);

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  const handleCourseClick = (id) => {
    navigate(`/my-courses/${id}`);
  };

  return (
    <div className="my-courses">
      <Navbar />
      <div className='my-courses-content'>
      <h1>Мои курсы</h1>
        <div className="courses-list">
          {enrollments.length > 0 ? (
            enrollments.map((course) => (
              <div className='course-card' key={course.id}>
                <h2>{course.title}</h2>
                <img src={math} alt={course.title} className="course-image" />
                <button onClick={() => handleCourseClick(course.id)} className='course-button'>
                  ПЕРЕЙТИ К ИЗУЧЕНИЮ
            </button>
          </div>
            ))
          ) : (
            <p>У вас пока нет курсов.</p>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default MyCourses;
