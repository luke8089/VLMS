-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 31, 2026 at 10:09 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `aura_edu`
--

-- --------------------------------------------------------

--
-- Table structure for table `answers`
--

CREATE TABLE `answers` (
  `id` int(11) NOT NULL,
  `submission_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `answer_text` text DEFAULT NULL,
  `selected_option` int(11) DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `ai_feedback` text DEFAULT NULL,
  `answered_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `answers`
--

INSERT INTO `answers` (`id`, `submission_id`, `question_id`, `answer_text`, `selected_option`, `is_correct`, `score`, `ai_feedback`, `answered_at`) VALUES
(154, 25, 265, NULL, 1, 1, 3, NULL, '2026-03-30 22:27:14'),
(155, 25, 266, NULL, 2, 1, 3, NULL, '2026-03-30 22:27:16'),
(156, 25, 267, NULL, 1, 1, 3, NULL, '2026-03-30 22:27:19'),
(157, 25, 268, NULL, 2, 0, 0, NULL, '2026-03-30 22:27:21'),
(158, 25, 269, NULL, 0, 1, 3, NULL, '2026-03-30 22:27:26'),
(159, 25, 270, 'fihm', NULL, 0, NULL, NULL, '2026-03-30 22:27:31'),
(160, 25, 271, NULL, 1, 0, 0, NULL, '2026-03-30 22:27:33'),
(161, 25, 272, NULL, 1, 0, 0, NULL, '2026-03-30 22:27:38'),
(162, 25, 273, 'dtux', NULL, 0, NULL, NULL, '2026-03-30 22:27:47'),
(163, 25, 274, NULL, 1, 0, 0, NULL, '2026-03-30 22:27:50');

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id` int(11) NOT NULL,
  `code` varchar(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `lecturer_id` int(11) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `is_published` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id`, `code`, `title`, `description`, `lecturer_id`, `category`, `is_published`, `created_at`, `updated_at`) VALUES
(1, 'BIT2210', 'Introduction to Programming ', 'learning basic programming and syntax', 3, 'Computer science ', 1, '2026-03-06 11:11:45', '2026-03-06 12:18:25'),
(2, 'BSCCS3425', 'Probability and statistics', 'its math', 3, 'Computer science ', 1, '2026-03-06 18:32:50', '2026-03-06 18:32:50'),
(3, 'BMA1234', 'Linear Mathematics', 'maths', 3, 'Information Technology', 1, '2026-03-10 06:50:48', '2026-03-10 06:50:48'),
(4, 'BMA2345', 'Calculas', 'tset', 3, 'Information Technology', 1, '2026-03-11 17:37:45', '2026-03-11 17:37:45'),
(5, 'BIT3219', 'object oriented programmming', 'this is a programming unit', 3, 'computer science', 1, '2026-03-26 11:26:08', '2026-03-26 11:26:08'),
(6, 'CSC103', 'Introduction to biology', 'this is pure a lab practical class', 3, 'Biology', 1, '2026-03-31 04:37:27', '2026-03-31 04:37:27');

-- --------------------------------------------------------

--
-- Table structure for table `enrollments`
--

CREATE TABLE `enrollments` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  `progress` float DEFAULT NULL,
  `status` enum('active','completed','dropped') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `enrollments`
--

INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `enrolled_at`, `progress`, `status`) VALUES
(1, 2, 1, '2026-03-06 12:18:57', 0, 'active'),
(2, 6, 1, '2026-03-06 18:28:54', 0, 'active'),
(3, 6, 2, '2026-03-06 18:39:05', 0, 'active'),
(4, 2, 2, '2026-03-10 06:45:03', 0, 'active'),
(5, 2, 3, '2026-03-10 06:53:04', 0, 'active'),
(6, 7, 1, '2026-03-11 17:30:47', 0, 'active'),
(7, 7, 2, '2026-03-11 17:30:51', 0, 'active'),
(8, 7, 3, '2026-03-11 17:30:54', 0, 'active'),
(9, 2, 4, '2026-03-11 17:41:42', 0, 'active'),
(10, 8, 4, '2026-03-12 11:51:52', 0, 'active'),
(11, 8, 1, '2026-03-12 11:51:54', 0, 'active'),
(12, 10, 4, '2026-03-18 12:14:44', 0, 'active'),
(13, 10, 1, '2026-03-18 12:16:19', 0, 'active'),
(14, 10, 3, '2026-03-18 12:16:34', 0, 'active'),
(15, 10, 2, '2026-03-18 12:16:35', 0, 'active'),
(16, 12, 1, '2026-03-26 11:21:43', 0, 'active'),
(17, 12, 3, '2026-03-26 11:21:57', 0, 'active'),
(18, 12, 5, '2026-03-26 11:35:27', 0, 'active'),
(19, 13, 1, '2026-03-30 21:35:40', 0, 'active'),
(20, 13, 5, '2026-03-30 21:35:40', 0, 'active'),
(21, 12, 4, '2026-03-30 22:30:14', 0, 'active'),
(22, 12, 2, '2026-03-30 22:30:19', 0, 'active'),
(23, 14, 6, '2026-03-31 04:48:45', 0, 'active');

-- --------------------------------------------------------

--
-- Table structure for table `exams`
--

CREATE TABLE `exams` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `exam_type` enum('quiz','midterm','final','assignment') DEFAULT NULL,
  `duration_minutes` int(11) NOT NULL,
  `total_marks` float NOT NULL,
  `passing_marks` float NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `is_proctored` tinyint(1) DEFAULT NULL,
  `is_published` tinyint(1) DEFAULT NULL,
  `shuffle_questions` tinyint(1) DEFAULT NULL,
  `allow_review` tinyint(1) DEFAULT NULL,
  `risk_threshold` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `grades_released` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `exams`
--

INSERT INTO `exams` (`id`, `course_id`, `title`, `description`, `exam_type`, `duration_minutes`, `total_marks`, `passing_marks`, `start_time`, `end_time`, `is_proctored`, `is_published`, `shuffle_questions`, `allow_review`, `risk_threshold`, `created_at`, `grades_released`) VALUES
(34, 3, 'Cat 1', '[assessment:cat1] Auto-generated from course materials. 10 questions pending review.', 'quiz', 60, 30, 15, '2026-03-31 01:27:00', '2026-03-31 02:27:00', 1, 1, 1, 0, 100, '2026-03-30 22:26:22', 1),
(35, 6, 'Cat 1', '[assessment:cat1] Auto-generated from course materials. 10 questions pending review.', 'quiz', 60, 30, 15, '2026-03-31 10:39:00', '2026-03-31 11:39:00', 1, 1, 1, 0, 100, '2026-03-31 07:38:11', 0);

-- --------------------------------------------------------

--
-- Table structure for table `face_admin_actions`
--

CREATE TABLE `face_admin_actions` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `action_type` enum('register_face','reset_face','verify_face','view_logs') NOT NULL,
  `reason` text DEFAULT NULL,
  `old_encoding` longblob DEFAULT NULL,
  `new_encoding` longblob DEFAULT NULL,
  `performed_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `face_verification_logs`
--

CREATE TABLE `face_verification_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `exam_id` int(11) DEFAULT NULL,
  `submission_id` int(11) DEFAULT NULL,
  `verification_type` enum('registration','pre_exam','liveness_check') NOT NULL,
  `status` enum('success','failed','pending') NOT NULL,
  `confidence_score` float DEFAULT NULL,
  `liveness_score` float DEFAULT NULL,
  `failure_reason` varchar(255) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `face_verification_logs`
--

INSERT INTO `face_verification_logs` (`id`, `user_id`, `exam_id`, `submission_id`, `verification_type`, `status`, `confidence_score`, `liveness_score`, `failure_reason`, `ip_address`, `user_agent`, `created_at`) VALUES
(3, 14, NULL, NULL, 'pre_exam', 'failed', 0.20336, 0.833333, 'Low confidence: 0.20', NULL, NULL, '2026-03-31 08:05:09');

-- --------------------------------------------------------

--
-- Table structure for table `learning_progress`
--

CREATE TABLE `learning_progress` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `material_id` int(11) NOT NULL,
  `progress_percent` float DEFAULT NULL,
  `time_spent_seconds` int(11) DEFAULT NULL,
  `last_accessed` datetime DEFAULT NULL,
  `completed` tinyint(1) DEFAULT NULL,
  `has_opened` tinyint(1) DEFAULT 0,
  `first_opened_at` datetime DEFAULT NULL,
  `last_page` int(11) DEFAULT 0,
  `total_pages` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `learning_progress`
--

INSERT INTO `learning_progress` (`id`, `student_id`, `material_id`, `progress_percent`, `time_spent_seconds`, `last_accessed`, `completed`, `has_opened`, `first_opened_at`, `last_page`, `total_pages`) VALUES
(6, 2, 11, 100, 60, '2026-03-30 21:51:46', 1, 1, '2026-03-24 12:05:05', 1, 1),
(7, 2, 10, 100, 0, '2026-03-24 19:16:35', 1, 1, '2026-03-24 19:16:35', 1, 1),
(8, 12, 12, 100, 675, '2026-03-26 12:26:34', 1, 1, '2026-03-26 11:36:39', 1, 1),
(9, 12, 9, 100, 15, '2026-03-26 15:24:12', 1, 1, '2026-03-26 15:23:56', 1, 1),
(10, 14, 14, 100, 300, '2026-03-31 07:36:36', 1, 1, '2026-03-31 07:13:52', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `lectures`
--

CREATE TABLE `lectures` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` text DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `is_published` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `lectures`
--

INSERT INTO `lectures` (`id`, `course_id`, `title`, `content`, `order_index`, `duration_minutes`, `is_published`, `created_at`) VALUES
(1, 1, 'Doc Arthur', '', 0, NULL, 1, '2026-03-06 11:16:58'),
(2, 2, 'Lec Shar', '', 0, NULL, 0, '2026-03-06 18:33:14'),
(3, 3, 'Mutheu', '', 0, NULL, 1, '2026-03-10 06:53:20'),
(4, 4, 'Thuo', '', 0, NULL, 1, '2026-03-11 17:38:05'),
(5, 6, 'lecturer Gladys', '', 0, NULL, 1, '2026-03-31 07:11:39');

-- --------------------------------------------------------

--
-- Table structure for table `live_classes`
--

CREATE TABLE `live_classes` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `meeting_link` varchar(500) NOT NULL,
  `platform` varchar(50) DEFAULT NULL,
  `scheduled_at` datetime NOT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `is_unlocked` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `materials`
--

CREATE TABLE `materials` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `lecture_id` int(11) DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `file_type` enum('pdf','video','slide','document','other') NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_size` int(11) DEFAULT NULL,
  `ai_summary` text DEFAULT NULL,
  `ai_flashcards` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ai_flashcards`)),
  `uploaded_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `materials`
--

INSERT INTO `materials` (`id`, `course_id`, `lecture_id`, `title`, `file_type`, `file_path`, `file_size`, `ai_summary`, `ai_flashcards`, `uploaded_at`) VALUES
(8, 2, NULL, 'Artificial intelligence .pdf', 'pdf', 'courses/2/Artificial_intelligence_f196f6b3.pdf', 0, 'Artificial intelligence (AI) has transformed various aspects of life, including healthcare, education, and business. Key concepts include machine learning algorithms that analyze vast amounts of data in seconds to improve efficiency, accuracy, and accessibility.\n\nIn education, AI-driven adaptive learning platforms personalize learning experiences for students worldwide, offering tailored content that enhances understanding and retention. Virtual tutors and AI-powered assistants make knowledge more accessible, particularly in regions with limited educational resources.\n\nThe business world is also experiencing a major shift due to AI innovation, with companies leveraging it for customer service through chatbots, predictive analytics, and automation of repetitive tasks. This allows employees to focus on creative and strategic work.\n\nHowever, the rise of AI raises important ethical and societal questions, including concerns about data privacy, bias in algorithms, and employment impacts. Governments, organizations, and individuals must collaborate to ensure that AI development is guided by fairness, transparency, and accountability, minimizing risks while fully harnessing its benefits.', NULL, '2026-03-24 11:52:14'),
(9, 1, NULL, 'Artificial intelligence .pdf', 'pdf', 'courses/1/Artificial_intelligence_fb2bb328.pdf', 0, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld. From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable. This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems. In the field of education, AI is personalizing learning experiences for students across the globe. As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds. The business world is also experiencing a major shift due to AI innovation. This allows employees to focus on mor e creative and strategic \nwork. Despite its many advantages, the rise of AI also raises important ethical and societal questions. Concerns about data privacy, bias in algorithms, and the impact on employment must be \ncarefully addressed. In doing so, society can fully harness the benefits of AI while minimizing its \nrisks.', NULL, '2026-03-24 11:53:13'),
(10, 3, NULL, 'Artificial intelligence .pdf', 'pdf', 'courses/3/Artificial_intelligence_e338fb57.pdf', 0, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld. From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable. Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions. This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.  \nIn the field of education, AI is personalizing learning experiences for students across the globe. \nAdaptive learning platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention. Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where educational resources are \nlimited. As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.  \nThe business world is also experiencing a major shift due to AI innovation. Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \nautomation of repetitive tasks. This allows employees to focus on mor e creative and strategic \nwork. At the same time, AI is driving the development of new industries and job roles, \nemphasizing the importance of digital skills and continuous learning in the modern workforce.  \nDespite its many advantages, the rise of AI also raises important ethical and societal questions. \nConcerns about data privacy, bias in algorithms, and the impact on employment must be \ncarefully addressed. As AI continues to evolve, it is crucial for govern ments, organizations, and \nindividuals to work together to ensure that its development is guided by fairness, transparency, \nand accountability. In doing so, society can fully harness the benefits of AI while minimizing', NULL, '2026-03-24 11:53:44'),
(11, 4, NULL, 'Artificial intelligence .pdf', 'pdf', 'courses/4/Artificial_intelligence_a9097e84.pdf', 0, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld. From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable. Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions. This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.  \nIn the field of education, AI is personalizing learning experiences for students across the globe. \nAdaptive learning platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention. Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where educational resources are \nlimited. As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.  \nThe business world is also experiencing a major shift due to AI innovation. Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \nautomation of repetitive tasks. This allows employees to focus on mor e creative and strategic \nwork. At the same time, AI is driving the development of new industries and job roles, \nemphasizing the importance of digital skills and continuous learning in the modern workforce.  \nDespite its many advantages, the rise of AI also raises important ethical and societal questions. \nConcerns about data privacy, bias in algorithms, and the impact on employment must be \ncarefully addressed. As AI continues to evolve, it is crucial for govern ments, organizations, and \nindividuals to work together to ensure that its development is guided by fairness, transparency, \nand accountability. In doing so, society can fully harness the benefits of AI while minimizing', NULL, '2026-03-24 11:54:19'),
(12, 5, NULL, 'Artificial_intelligence_a9097e84.pdf', 'pdf', 'courses/5/Artificial_intelligence_a9097e84_8ed21b57.pdf', 0, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld. From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable. This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems. In the field of education, AI is personalizing learning experiences for students across the globe. As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds. The business world is also experiencing a major shift due to AI innovation. This allows employees to focus on mor e creative and strategic \nwork. Despite its many advantages, the rise of AI also raises important ethical and societal questions. Concerns about data privacy, bias in algorithms, and the impact on employment must be \ncarefully addressed. In doing so, society can fully harness the benefits of AI while minimizing its \nrisks.', NULL, '2026-03-26 11:29:10'),
(14, 6, NULL, 'Artificial intelligence .pdf', 'pdf', 'courses/6/Artificial_intelligence_6c291ac6.pdf', 0, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld. From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable. This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems. In the field of education, AI is personalizing learning experiences for students across the globe. As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds. The business world is also experiencing a major shift due to AI innovation. This allows employees to focus on mor e creative and strategic \nwork. Despite its many advantages, the rise of AI also raises important ethical and societal questions. Concerns about data privacy, bias in algorithms, and the impact on employment must be \ncarefully addressed. In doing so, society can fully harness the benefits of AI while minimizing its \nrisks.', NULL, '2026-03-31 07:13:20');

-- --------------------------------------------------------

--
-- Table structure for table `questions`
--

CREATE TABLE `questions` (
  `id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `question_text` text NOT NULL,
  `question_type` enum('mcq','short_answer','essay') NOT NULL,
  `options` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`options`)),
  `correct_answer` text DEFAULT NULL,
  `marks` float NOT NULL,
  `difficulty` enum('remember','understand','apply','analyze','evaluate','create') DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `explanation` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `questions`
--

INSERT INTO `questions` (`id`, `exam_id`, `question_text`, `question_type`, `options`, `correct_answer`, `marks`, `difficulty`, `order_index`, `explanation`) VALUES
(265, 34, 'Fill in the blank: Adaptive _____ platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention.', 'mcq', '[\"education\", \"learning\", \"algorithms\", \"world\"]', '1', 3, 'understand', 0, 'Adaptive learning platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention.'),
(266, 34, 'Fill in the blank: The business _____ is also experiencing a major shift due to AI innovation.', 'mcq', '[\"education\", \"algorithms\", \"world\", \"learning\"]', '2', 3, 'understand', 1, 'The business world is also experiencing a major shift due to AI innovation.'),
(267, 34, 'Fill in the blank: Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where _____al resources are \nlimited.', 'mcq', '[\"education\", \"world\", \"learning\", \"algorithms\"]', '0', 3, 'understand', 2, 'Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where educational resources are \nlimited.'),
(268, 34, 'Fill in the blank: From healthcare to _____, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 'mcq', '[\"learning\", \"algorithms\", \"world\", \"education\"]', '3', 3, 'understand', 3, 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(269, 34, 'Fill in the blank: As a result, _____ is becoming more inclusive, flexible, and responsive to individual \nneeds.', 'mcq', '[\"learning\", \"world\", \"algorithms\", \"education\"]', '0', 3, 'understand', 4, 'As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.'),
(270, 34, 'Describe learning.', 'short_answer', 'null', 'In the field of education, AI is personalizing learning experiences for students across the globe.', 3, 'understand', 5, 'Reference: In the field of education, AI is personalizing learning experiences for students across the globe.'),
(271, 34, 'Fill in the blank: Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \n_____ of repetitive tasks.', 'mcq', '[\"education\", \"learning\", \"world\", \"automation\"]', '3', 3, 'understand', 6, 'Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \nautomation of repetitive tasks.'),
(272, 34, 'Fill in the blank: This wave of _____ is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.', 'mcq', '[\"education\", \"world\", \"learning\", \"innovation\"]', '3', 3, 'understand', 7, 'This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.'),
(273, 34, 'Explain world in your own words.', 'short_answer', 'null', 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.', 3, 'understand', 8, 'Reference: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(274, 34, 'Fill in the blank: In the field of education, AI is personalizing _____ experiences for students across the globe.', 'mcq', '[\"world\", \"algorithms\", \"education\", \"learning\"]', '3', 3, 'understand', 9, 'In the field of education, AI is personalizing learning experiences for students across the globe.'),
(275, 35, 'Explain education in your own words.', 'short_answer', 'null', 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 3, 'understand', 0, 'Reference: From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(276, 35, 'Describe world.', 'short_answer', 'null', 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.', 3, 'understand', 1, 'Reference: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(277, 35, 'Fill in the blank: The business _____ is also experiencing a major shift due to AI innovation.', 'mcq', '[\"innovation\", \"learning\", \"world\", \"education\"]', '2', 3, 'understand', 2, 'The business world is also experiencing a major shift due to AI innovation.'),
(278, 35, 'Fill in the blank: This wave of _____ is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.', 'mcq', '[\"education\", \"world\", \"innovation\", \"learning\"]', '2', 3, 'understand', 3, 'This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.'),
(279, 35, 'Fill in the blank: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \n_____.', 'mcq', '[\"innovation\", \"learning\", \"world\", \"education\"]', '2', 3, 'understand', 4, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(280, 35, 'Explain Artificial in your own words.', 'short_answer', 'null', 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.', 3, 'understand', 5, 'Reference: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(281, 35, 'Explain innovation in your own words.', 'short_answer', 'null', 'This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.', 3, 'understand', 6, 'Reference: This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.'),
(282, 35, 'Fill in the blank: From healthcare to _____, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 'mcq', '[\"innovation\", \"education\", \"world\", \"learning\"]', '1', 3, 'understand', 7, 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(283, 35, 'Fill in the blank: As a result, _____ is becoming more inclusive, flexible, and responsive to individual \nneeds.', 'mcq', '[\"world\", \"innovation\", \"education\", \"learning\"]', '3', 3, 'understand', 8, 'As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.'),
(284, 35, 'Describe learning.', 'short_answer', 'null', 'In the field of education, AI is personalizing learning experiences for students across the globe.', 3, 'understand', 9, 'Reference: In the field of education, AI is personalizing learning experiences for students across the globe.');

-- --------------------------------------------------------

--
-- Stand-in structure for view `student_face_status`
-- (See below for the actual view)
--
CREATE TABLE `student_face_status` (
`student_id` int(11)
,`email` varchar(120)
,`first_name` varchar(50)
,`last_name` varchar(50)
,`department` varchar(100)
,`face_status` varchar(14)
,`total_exams` bigint(21)
,`verified_exams` decimal(22,0)
,`last_verification_date` datetime
);

-- --------------------------------------------------------

--
-- Table structure for table `submissions`
--

CREATE TABLE `submissions` (
  `id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `total_score` float DEFAULT NULL,
  `is_graded` tinyint(1) DEFAULT NULL,
  `is_flagged` tinyint(1) DEFAULT NULL,
  `risk_score` int(11) DEFAULT NULL,
  `status` enum('in_progress','submitted','graded') DEFAULT NULL,
  `face_verified` tinyint(1) DEFAULT NULL,
  `approval_status` enum('pending','approved','cancelled') DEFAULT 'pending',
  `face_verified_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `submissions`
--

INSERT INTO `submissions` (`id`, `exam_id`, `student_id`, `started_at`, `submitted_at`, `total_score`, `is_graded`, `is_flagged`, `risk_score`, `status`, `face_verified`, `approval_status`, `face_verified_at`) VALUES
(25, 34, 12, '2026-03-30 22:27:02', '2026-03-30 22:27:50', 12, 1, 0, 35, 'graded', 1, 'approved', NULL),
(26, 35, 14, '2026-03-31 07:39:09', NULL, NULL, 0, 0, 20, 'in_progress', 1, 'pending', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `role` enum('admin','lecturer','student') NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `profile_image` varchar(255) DEFAULT NULL,
  `face_encoding` blob DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_expires` datetime DEFAULT NULL,
  `share_contact` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `first_name`, `last_name`, `role`, `department`, `profile_image`, `face_encoding`, `is_active`, `created_at`, `updated_at`, `phone_number`, `bio`, `reset_token`, `reset_token_expires`, `share_contact`) VALUES
(2, 'user@gmail.com', '$2b$12$LaHTXM/ifCNNtJL5yEeIK.E8FAT.BO2qGLOV0jNItK1MAs.KOfyN2', 'user', 'user', 'student', NULL, 'profiles/_26f3864c.jpg', 0x8004958c040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b0074946289420004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000066150f3b66150f3b66158f3b33c73e3b33c73e3c33c7be3bc0da323cf328033c4deea63c8d8c623c00796e3c6dbdc43c2d1f093dd9019b3cd9011b3da00b153dbd06183d491a0c3dd9011b3df6fc1d3da987653dddd5353df328833d369b593d86e4ac3d66158f3ddb6ba83dd9019b3dc3aecd3df866ab3df866ab3dc0dab23df9d0b83d8b22d53df9d0b83d512ccf3df9d0b83dc682e83d6e27d23d1836c93dd62d003ea987e53df328033e3805e73d857a1f3e71fbec3d4b84193e81a6043e491a0c3e2e89163e66150f3e9060fd3d67ca153ebc51113ef592103e6560083e11d90c3e6560083e491a0c3ef4dd093ebb9c0a3ed8970d3e9f560e3ec8ecf53dbb9c0a3eabf1f23dbb9c0a3e9dec003ef328033efe0ee13d1edefe3d6e27d23d5396dc3d396ff43d89b8c73da549bd3de37deb3df866ab3d4deea63d2e89963d1562ae3d857a9f3da3dfaf3da175a23d857a9f3d69e9a93dfb3ac63dbd06983d9ea1873d66158f3da00b953df328833df592903da987653d857a9f3ddb6ba83d70915f3d89b8473d73657a3d33c73e3dc3ae4d3de0a9503d53965c3d53965c3d19a0563d86e42c3da00b153d491a0c3da00b153dd9011b3d7365fa3c8310123d396ff43c396ff43c8d8ce23cd62d003d0079ee3c8d8c623c19a0d63c33c7be3cf9d0b83c13f8a03c6dbdc43c73657a3c66158f3c2d1f893ca6b3ca3c66158f3cf9d0b83c2d1f893c4deea63c73657a3cf328833c4dee263c8d8c623cd9011b3cf328833ca6b34a3c73657a3c8d8c623cf328833cc0da323c19a0d63bc0da323c8d8c623c66150f3c2d1f893c00796e3c2d1f893cd9019b3cd9011b3c33c73e3c2d1f893c0079ee3b00796e3c66158f3c73657a3c00796e3c19a0563c4dee263c00796e3c33c73e3c19a0563c19a0563c4deea63c66158f3c6dbdc43cd9019b3c13f8a03ca6b34a3c73657a3c4deea63c66158f3c19a0563cf9d0b83ca00b953c73657a3c00796e3c13f8a03c4deea63cc682e83cf9d0b83c0079ee3cf9d0b83c396ff43c8d8ce23ca6b3ca3cf328033dc682e83c33c7be3cc3ae4d3d7365fa3cf6fc1d3dd9011b3d8310123dc0da323d4dee263dc0da323dfda4533df6fc1d3df6fc1d3d2d1f093dc3ae4d3d8310123dc0da323d396ff43ca6b3ca3c86e42c3d69e9293d33c7be3c69e9293d491a0c3dddd5353d30f3233d50c2413de0a9d03cc0da323d8310123dd62d003dbd06183d1024063dc0dab23c2d1f093d6dbdc43c6dbdc43ca6b3ca3ca00b953c86e4ac3c6dbdc43c00796e3cf9d0b83c33c73e3c19a0563cf328033cc0da323c33c73e3c4dee263c4dee263c33c7be3b19a0d63b66150f3b33c7be3b66150f3b33c73e3b947494622e, 1, '2026-03-06 10:55:03', '2026-03-30 18:54:15', '0746075436', 'i love books', NULL, NULL, 0),
(3, 'lec@gmail.com', '$2b$12$o6J7..Zl4B0p57BWzHoiZ.Nh72VD04jF5WfJ/qEwFdYy0eXMW15Hi', 'Dr Lec', 'Rich', 'lecturer', NULL, 'profiles/_a6d187e9.jpg', NULL, 1, '2026-03-06 11:10:31', '2026-03-25 07:07:19', '0700000000', 'i love teaching', NULL, NULL, 1),
(5, 'admin@gmail.com', '$2b$12$f92QtBuhZmNPTYm8SPWVGesAvRzyYPb7221wqkEuuJ9zTKp1p5oj2', 'admin', 'admin', 'admin', NULL, NULL, NULL, 1, '2026-03-06 12:16:12', '2026-03-06 12:16:12', NULL, NULL, NULL, NULL, 0),
(6, 'jane123@gmail.com', '$2b$12$vWbZld8Tv8v56/uE4bFGxenUs/qzxwdhRc9h5UjbGyK6.PtxA1Sfi', 'jane ', 'doe', 'student', NULL, 'profiles/qr-code_53137d96.png', NULL, 1, '2026-03-06 18:25:58', '2026-03-06 18:53:52', '0799009660', 'i am a nursing student', NULL, NULL, 1),
(7, 'edwinmeiteikini@gmail.com', '$2b$12$4EJ1cCXc1Min23ICXQzykeDs57BfZq2BDKnL.G5zOl0uLmNvQI0c.', 'Edwin', 'Meiteikini', 'student', NULL, 'profiles/download_1_23a85ef9.jpg', 0x8004958d040000000000008c166e756d70792e5f636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b0074946289420004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007366ac3a73662c3ad64c013ba5d9963b73662c3b0ca0213c3d138c3c43e3dc3c1270f23cdba4443d7746623d0d18af3dda2cb73da9b9cc3d103cde3d11f8e43d3d57053e0bca103e11f8e43d0b28143e71180e3e0a6c0d3e7176113e0c5c283ea651243ea66b2e3ea5f3203e0c5c283edace333e0e32393e0f664d3e0d76323ea651243e0a6c0d3e0be41a3e3f03273e0b86173e71180e3e3d130c3e3e8b193e1270f23ddbe8bd3d43e3dc3da841bf3da7c9b13d7366ac3ddc1cd23da8fdc53d7322b33d7322b33dd9f8a23dda2cb73dd880953d0dd4b53da785b83dd83c9c3d3d57853dd83c9c3dda70b03d0a6c8d3d71ba8a3d0a6c8d3d71ba8a3d445b6a3dde0c6d3d43e35c3d76ce543da9b94c3daba9673ddba4443d13e87f3d426b4f3d41f3413da7c9313d41f3413d43e35c3d7556473ddba4443ddba4443d1080573d3e8b193d407b343d0e903c3d0d182f3d0ab0063dd7c40e3d70fe033d1270f23c7176113d3f03a73c7556c73cd64c013d41f3c13cda2cb73c0ca0a13c0ca0a13c7556c73cd64c813cda2cb73c7176913c3d138c3c0ab0863ca9b94c3cd83c9c3cd83c9c3c41f3c13cd83c9c3c7556c73c45d3f73ca7c9b13c0ab0863c45d3773c0ab0863cd64c813ca9b94c3cda2c373c3f03a73c0e90bc3ca9b9cc3cd83c9c3c0ca0a13c73662c3ca9b94c3c0ab0863c7746623c7366ac3cdc1cd23cd64c013d0e90bc3c7556c73c1080d73c41f3c13ca7c9b13ca651243d41f3c13c1080d73c3d130c3d7176113ddf847a3d7746623d0b28943d7232983da785b83da785b83d426bcf3dd9b4a93d71ba8a3d71ba8a3d79367d3d79367d3d0f084a3daba9673d3ecf923d1270723daa315a3d70fe833da9b94c3dda2c373d0f084a3d70fe033d70fe033d7176113ddc1cd23cd83c1c3d7176113da461093daba9e73cde0ced3c0ab0063d0ca0a13c7556c73c0e90bc3c43e3dc3c1270f23c7556c73c41f3c13c0e90bc3ca5d9163d41f3c13c7556c73caba9e73cd83c9c3cd64c813c1080573c0ca0213c3d130c3c7746623c41f3c13bde0ced3b1080573c73662c3c1080d73b73662c3ca5d9163cde0ced3b1080573b41f3c13bd64c813b7366ac3a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000947494622e, 1, '2026-03-11 17:26:40', '2026-03-11 17:35:04', '+254746075436', 'i like computer science', NULL, NULL, 0),
(8, 'hakeem@gmail.com', '$2b$12$B0NTCGY1kWf1dAjmLqse5.G8ioLCwpjC5zFnEkybfZlQUDIih.nN.', 'hakeem', 'ibrahim', 'student', NULL, 'profiles/Screenshot_2026-03-11_133720_02714813.png', NULL, 1, '2026-03-12 11:49:52', '2026-03-12 11:51:22', '+254746075436', 'tester', NULL, NULL, 0),
(9, 'actor@gmail.com', '$2b$12$qTNogxKhphinD4cn6y4C8uuftllsKAJe7iChiBwycEojHACJaRp12', 'actor ', 'actor ', 'student', NULL, NULL, NULL, 1, '2026-03-12 12:20:21', '2026-03-12 12:20:21', NULL, NULL, NULL, NULL, 0),
(10, 'wahbih837@gmail.com', '$2b$12$Azu1.hUN/N/xLpmDRkTbmeSaCF0SB.DssoJ9969Oeu7PnbMAO9EnG', 'wahbi', 'hassan', 'student', NULL, 'profiles/Computer_Graphics_Assignment_ac52846a.png', NULL, 1, '2026-03-18 12:10:12', '2026-03-18 12:11:17', NULL, NULL, NULL, NULL, 0),
(11, 'janny@gmail.com', '$2b$12$v/D/yHUFQyKpFb7T4Vqq6u6Q.EcKqcAm9b47/7oyRiLHnFARQY8Za', 'janny', 'dae', 'student', NULL, NULL, NULL, 1, '2026-03-26 11:18:24', '2026-03-26 11:18:24', NULL, NULL, NULL, NULL, 0),
(12, 'Jane@gmail.com', '$2b$12$7UiQPnSKvH1A6EmPOXdr5eXC9GUpaxwVFJN11n3oY4PwzZmgH2fy6', 'jane', 'Doe', 'student', 'Computer Science', 'profiles/_92bafaff.jpg', 0x8004958c040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b00749462894200040000000000000000000000000000000000000000000000000000000000000000000000000000ae3b383a00000000ae3b383aae3b383ac22c8a3bae3b383b3834a13b24434f3c2443cf3b7db0153c8bfdbd3c24434f3cae3b383c8bfdbd3ce56a843c4681c93c4681c93c7db0953ce56a043d5b721b3dbc88e03c69bf433db10d0d3d8bfdbd3c4681493d6c91183d2443cf3c35624c3d7db0153d7ade403dcda75d3dbc88603ddfc65a3dd2e29c3df520973d58a0c63d3562cc3d66edee3d54cef13d30d9173ec1c31f3e850b1f3ef520173ebf5a353e37cb363e95c1313e6a282e3e95c1313e1fba1a3e7ade403e2f702d3ec7b53e3e8fcf123ed179323e4a531e3ea0ee0f3e8fcf123e2123053eba1ff63d9893063e6756d93d882be93d009cea3d7975d63df3b7ac3d22dae43ddfc6da3d8bfdbd3d8a94d33dbef1ca3d6c91983dae3bb83d8d66a83d0105d53d69bfc33d37cbb63d4bbc883d3834a13d7db0953dd179b23d0640943d6c91983df689813d0f527d3d66ed6e3dc22c8a3d21717a3de56a843db10d8d3d5b729b3d3290773d3290773dd44b873da0ee8f3d54ce713d7f19803dd44b873d6c91983d0105553d21717a3d4bbc883ddfc65a3d770c6c3d43af743dae3b383d7ade403d2715243d58a0463d0f52fd3c8bfd3d3d0105d53c2715243df3b72c3d2715243df689013df3b72c3d2715243dd44b073d04d7293d58a0463dae3bb83ca0ee0f3da0ee0f3ddfc6da3ce56a043dc22c0a3dc22c8a3c7db0153d2443cf3c0f52fd3ca0ee0f3d5b721b3d0105d53cd44b073dbc88e03c54cef13cf689013d3290f73cd44b073dc22c0a3d7db0953cc22c0a3d4681c93cae3bb83c6c91183d6c91183d54cef13c54cef13c7db0953c770cec3c9a4ae63c770cec3cc22c0a3d2443cf3c3290f73ce56a043d3290f73cdfc6da3cae3bb83c2443cf3c3834a13c2443cf3cf3b7ac3cdfc6da3c0f527d3cdfc6da3c54ce713c0f527d3c0105d53c16f6a63c5b729b3cd179b23c3834a13c0105d53c7db0953c0f527d3c69bfc33c5b729b3c54ce713c54ce713c54ce713c0f527d3c0f527d3c9a4a663c24434f3c69bf433cae3b383c24434f3c7db0153c54ce713c3834213cf3b72c3cdfc65a3c9a4a663c7db0953c54ce713ca0ee8f3cdfc65a3c3834213c69bf433cae3b383c7db0153c3834213cdfc65a3cae3b383c24434f3c0f527d3c69bf433c24434f3cae3b383c2443cf3b69bf433cdfc65a3cae3b383c24434f3c9a4a663c69bf433c3834213cc22c8a3c0f527d3cae3bb83b54ce713c9a4a663cdfc65a3c0f527d3c7db0953c24434f3cae3bb83c54ce713cbc88e03c16f6a63c5b721b3d8fcf123d175f913d8bfd3d3ddfc65a3d58a0463df0e5573d8fcf123d3290f73ce56a843c5b729b3c0f52fd3b24434f3c9a4ae63b7db0153cc22c0a3b947494622e, 1, '2026-03-26 11:19:54', '2026-03-31 04:48:08', '+254797242328', 'i am a computer science student intrested in improving my academic performance', NULL, NULL, 0),
(13, 'test@student.com', '$2b$12$tZJOslM7p2cIVnuS6FqgsOMYC6oMd0R4Wr4sPo0RfEym4Sjew5Ftu', 'Test', 'Student', 'student', NULL, NULL, NULL, 1, '2026-03-30 21:35:22', '2026-03-30 21:35:22', NULL, NULL, NULL, NULL, 0),
(14, 'student@gmail.com', '$2b$12$S81MD6168BT28Y.pvHDzbu6tgDfdR7cDVeo0I/1Oni69r.Fy6qQDG', 'student', 'student ', 'student', 'Biology', 'profiles/_4aea87bd.jpg', 0x8004958c040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b007494628942000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000850d813980f8ff397d5b403ab5bffe3980f8ff39f7d57d393ca39f3af7d57d394f66203bbecf0f3b6d8b0f3b15e30f3ba54a3f3be3a97f3b0fe1873b7d8aaf3b94be5f3b15b8c73b80ded73b34e8333c071d283c5012483cdffa273cb43b243c0e3d203cb0ed473c599e4b3c27f7ab3c5b97673c5d257c3c500b823c7d028a3cfd1f683cd556ae3c89bea53cb539bc3c4cecb93c75f9d73c99efc53cf51a083d1814dc3cf1db0d3dcbfc1a3df0eb313d57ca333dd3ed4c3d6fd24a3daddc893dfcbc743d674c923d1340973de453b43dbb58973dccaebf3dd4b7c33d8cc6e83d7464e43d302d013e5dcbfe3dc6530c3e35fee43df7e2213eb82d083e2970153e3f080b3e6302183ebbef0e3e00b8153e40730a3ea942123e29b9083e43a7053e25bd0c3e99b30a3ea04df63d08dbfb3d24c10b3ea7a7023edb1f033e7819073e3373f43dd56a053e09defc3d1f63f03d585aef3db5f3fc3d0564f13de3d1f13dd873f33d7800063e8fd9ef3d3b5ef13dd3efd13d05cae33d07c6db3d10dbd13d4dd1d13ddb5fd03defc6be3d3d3dd53de356c03d2b4fb93d6de0ae3da562b03d84cd7f3dc1e69c3d316e8a3d036b993de3b6743de7629e3db0da683da3f8823d41ac4d3d98ff3f3d38c94c3defcf4c3d93e32b3da305393d59dc323d80cd2d3d11ef2d3dd4f1563d7bd9373d85f7283ddcf93e3d7dde313d0fbd2f3db8c2583d7bb82e3d14f2263dede92c3d60e1373d9d00343d48f7393d7403313d1040533d58ec2c3df1f31b3d1bef223dd31b3c3de409133d70f72a3d7015133ddb562e3df00c083d27ec3d3db815143d2b132c3d640a013d3042fa3c8fe60e3d4fcfeb3c93f10e3da1f2143d59db0d3d59000b3dd6d20d3d05b7f93cdbafe33c11e6013d04e9033d30d7db3cb9c1dd3c78f2f33cccc8e53cf0f1db3c01faeb3c58dce53c60f3e93c3ddf053d980cbc3c4411063dd500d43c93fcf93ccba2ff3ca323f63c31d0133d77ec0b3d4fe1083decdc293dc0e9153d85ef0b3db4c3073d13e73a3d9bd0193d69c91e3ddee7173d4f19333deeea173d89f71d3d1bc3fd3c38010c3d4761e63cebd2123d6d12fe3cc9fa0c3d0554e23c0bef103de13de63ca7ee0a3d2b1be43c44ff043de3fec33c54d9113da5dde13c47c8f53c07f4d13cd1e2d93cc0a3c93c3fd2db3c90b6cf3ca7a4c33cbf12a63c00d2bb3c30e59f3c3dd8b73c540ec23ccef9a33c09f4973c6bdf933c710a9e3cb58dd13c17cb873c65aab93c8117823cbdefab3cf038843c960a843c34359a3c5d2a963cc039a23c3105023d9a37113d7022333d0df82c3dad97c53cb4eebd3cb70b303c4e1e003c947494622e, 1, '2026-03-30 22:39:49', '2026-03-31 08:01:46', '0746075436', 'the best', NULL, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `user_analytics`
--

CREATE TABLE `user_analytics` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) DEFAULT NULL,
  `metric_type` varchar(50) NOT NULL,
  `metric_value` float DEFAULT NULL,
  `metadata_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata_json`)),
  `recorded_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `violations`
--

CREATE TABLE `violations` (
  `id` int(11) NOT NULL,
  `submission_id` int(11) NOT NULL,
  `violation_type` enum('multiple_faces','no_face','eye_gaze','head_pose','lip_movement','phone_detected','tab_switch','background_person','other') NOT NULL,
  `severity` int(11) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `screenshot_path` varchar(500) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `video_path` varchar(500) DEFAULT NULL,
  `video_format` varchar(50) DEFAULT NULL,
  `video_duration` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `violations`
--

INSERT INTO `violations` (`id`, `submission_id`, `violation_type`, `severity`, `description`, `screenshot_path`, `timestamp`, `video_path`, `video_format`, `video_duration`) VALUES
(445, 25, 'no_face', 15, 'No face detected in frame', NULL, '2026-03-30 22:27:41', 'clip_445_20260330_222749.webm', 'video/webm', 8),
(446, 25, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-30 22:27:50', NULL, NULL, NULL),
(447, 25, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-30 22:27:51', NULL, NULL, NULL),
(448, 26, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-31 07:39:23', NULL, NULL, NULL),
(449, 26, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-31 07:39:24', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Structure for view `student_face_status`
--
DROP TABLE IF EXISTS `student_face_status`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `student_face_status`  AS SELECT `u`.`id` AS `student_id`, `u`.`email` AS `email`, `u`.`first_name` AS `first_name`, `u`.`last_name` AS `last_name`, `u`.`department` AS `department`, CASE WHEN `u`.`face_encoding` is not null THEN 'registered' ELSE 'not_registered' END AS `face_status`, count(distinct `s`.`id`) AS `total_exams`, sum(case when `s`.`face_verified` = 1 then 1 else 0 end) AS `verified_exams`, max(`fvl`.`created_at`) AS `last_verification_date` FROM ((`users` `u` left join `submissions` `s` on(`u`.`id` = `s`.`student_id`)) left join `face_verification_logs` `fvl` on(`u`.`id` = `fvl`.`user_id` and `fvl`.`verification_type` = 'pre_exam' and `fvl`.`status` = 'success')) WHERE `u`.`role` = 'student' GROUP BY `u`.`id`, `u`.`email`, `u`.`first_name`, `u`.`last_name`, `u`.`department`, `u`.`face_encoding` ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `answers`
--
ALTER TABLE `answers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `submission_id` (`submission_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `lecturer_id` (`lecturer_id`);

--
-- Indexes for table `enrollments`
--
ALTER TABLE `enrollments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_enrollment` (`student_id`,`course_id`),
  ADD KEY `course_id` (`course_id`);

--
-- Indexes for table `exams`
--
ALTER TABLE `exams`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `idx_exams_course_created` (`course_id`,`created_at`);

--
-- Indexes for table `face_admin_actions`
--
ALTER TABLE `face_admin_actions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_student_id` (`student_id`),
  ADD KEY `idx_admin_id` (`admin_id`);

--
-- Indexes for table `face_verification_logs`
--
ALTER TABLE `face_verification_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_exam_id` (`exam_id`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `fk_face_logs_submission` (`submission_id`);

--
-- Indexes for table `learning_progress`
--
ALTER TABLE `learning_progress`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_learning_progress` (`student_id`,`material_id`),
  ADD KEY `material_id` (`material_id`);

--
-- Indexes for table `lectures`
--
ALTER TABLE `lectures`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`);

--
-- Indexes for table `live_classes`
--
ALTER TABLE `live_classes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`);

--
-- Indexes for table `materials`
--
ALTER TABLE `materials`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `lecture_id` (`lecture_id`);

--
-- Indexes for table `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `exam_id` (`exam_id`);

--
-- Indexes for table `submissions`
--
ALTER TABLE `submissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_submission` (`exam_id`,`student_id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `idx_submissions_exam_status_graded` (`exam_id`,`status`,`is_graded`),
  ADD KEY `idx_submissions_exam_flagged` (`exam_id`,`is_flagged`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_email` (`email`),
  ADD KEY `idx_reset_token` (`reset_token`);

--
-- Indexes for table `user_analytics`
--
ALTER TABLE `user_analytics`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `course_id` (`course_id`);

--
-- Indexes for table `violations`
--
ALTER TABLE `violations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `submission_id` (`submission_id`),
  ADD KEY `idx_violations_submission_timestamp` (`submission_id`,`timestamp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `answers`
--
ALTER TABLE `answers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=164;

--
-- AUTO_INCREMENT for table `courses`
--
ALTER TABLE `courses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `enrollments`
--
ALTER TABLE `enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `exams`
--
ALTER TABLE `exams`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `face_admin_actions`
--
ALTER TABLE `face_admin_actions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `face_verification_logs`
--
ALTER TABLE `face_verification_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `learning_progress`
--
ALTER TABLE `learning_progress`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `lectures`
--
ALTER TABLE `lectures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `live_classes`
--
ALTER TABLE `live_classes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `materials`
--
ALTER TABLE `materials`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `questions`
--
ALTER TABLE `questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=285;

--
-- AUTO_INCREMENT for table `submissions`
--
ALTER TABLE `submissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `user_analytics`
--
ALTER TABLE `user_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `violations`
--
ALTER TABLE `violations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=450;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `answers`
--
ALTER TABLE `answers`
  ADD CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`submission_id`) REFERENCES `submissions` (`id`),
  ADD CONSTRAINT `answers_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`);

--
-- Constraints for table `courses`
--
ALTER TABLE `courses`
  ADD CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `enrollments`
--
ALTER TABLE `enrollments`
  ADD CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `exams`
--
ALTER TABLE `exams`
  ADD CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `face_admin_actions`
--
ALTER TABLE `face_admin_actions`
  ADD CONSTRAINT `fk_face_admin_admin` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_face_admin_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `face_verification_logs`
--
ALTER TABLE `face_verification_logs`
  ADD CONSTRAINT `fk_face_logs_exam` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_face_logs_submission` FOREIGN KEY (`submission_id`) REFERENCES `submissions` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_face_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `learning_progress`
--
ALTER TABLE `learning_progress`
  ADD CONSTRAINT `learning_progress_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `learning_progress_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`);

--
-- Constraints for table `lectures`
--
ALTER TABLE `lectures`
  ADD CONSTRAINT `lectures_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `live_classes`
--
ALTER TABLE `live_classes`
  ADD CONSTRAINT `live_classes_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `materials`
--
ALTER TABLE `materials`
  ADD CONSTRAINT `materials_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  ADD CONSTRAINT `materials_ibfk_2` FOREIGN KEY (`lecture_id`) REFERENCES `lectures` (`id`);

--
-- Constraints for table `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`);

--
-- Constraints for table `submissions`
--
ALTER TABLE `submissions`
  ADD CONSTRAINT `submissions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`),
  ADD CONSTRAINT `submissions_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_analytics`
--
ALTER TABLE `user_analytics`
  ADD CONSTRAINT `user_analytics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_analytics_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `violations`
--
ALTER TABLE `violations`
  ADD CONSTRAINT `violations_ibfk_1` FOREIGN KEY (`submission_id`) REFERENCES `submissions` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
