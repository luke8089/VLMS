-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 01, 2026 at 01:52 AM
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
(184, 36, 350, 'test', NULL, 0, NULL, NULL, '2026-03-31 22:35:57'),
(185, 36, 351, 'test', NULL, 0, NULL, NULL, '2026-03-31 22:36:02'),
(186, 36, 352, NULL, 1, 0, 0, NULL, '2026-03-31 22:36:05'),
(187, 36, 353, NULL, 1, 0, 0, NULL, '2026-03-31 22:36:07'),
(188, 36, 354, NULL, 2, 1, 3, NULL, '2026-03-31 22:36:09'),
(189, 36, 355, NULL, 1, 1, 3, NULL, '2026-03-31 22:36:11'),
(190, 36, 356, NULL, 2, 0, 0, NULL, '2026-03-31 22:36:30'),
(191, 36, 357, 'test', NULL, 1, 3, NULL, '2026-03-31 22:36:35'),
(192, 36, 358, NULL, 2, 1, 3, NULL, '2026-03-31 22:36:37'),
(193, 36, 359, NULL, 1, 1, 3, NULL, '2026-03-31 22:36:39'),
(194, 37, 360, 'test', NULL, 1, 3, NULL, '2026-03-31 22:47:14'),
(195, 37, 361, 'test', NULL, 1, 3, NULL, '2026-03-31 22:47:19'),
(196, 37, 362, NULL, 0, 1, 3, NULL, '2026-03-31 22:47:23'),
(197, 37, 363, NULL, 2, 1, 3, NULL, '2026-03-31 22:47:27'),
(198, 37, 364, 'test', NULL, 1, 3, NULL, '2026-03-31 22:47:38'),
(199, 37, 365, NULL, 0, 1, 3, NULL, '2026-03-31 22:47:41'),
(200, 37, 366, NULL, 1, 0, 0, NULL, '2026-03-31 22:47:43'),
(201, 37, 367, 'test', NULL, 0, NULL, NULL, '2026-03-31 22:47:47'),
(202, 37, 368, NULL, 0, 0, 0, NULL, '2026-03-31 22:47:49'),
(203, 37, 369, NULL, 1, 0, 0, NULL, '2026-03-31 22:47:52');

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
(23, 14, 6, '2026-03-31 04:48:45', 0, 'active'),
(24, 15, 3, '2026-03-31 12:37:04', 0, 'active'),
(25, 15, 4, '2026-03-31 12:37:25', 0, 'active');

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
(43, 3, 'Cat 1', '[assessment:cat1] Auto-generated from course materials. 10 questions pending review.', 'quiz', 60, 30, 15, NULL, NULL, 1, 1, 1, 0, 100, '2026-03-31 21:25:09', 0),
(44, 3, 'Cat 2', '[assessment:cat2] Auto-generated from course materials. 10 questions pending review.', 'midterm', 60, 30, 15, '2026-04-01 01:46:00', '2026-04-01 02:46:00', 1, 1, 1, 0, 100, '2026-03-31 22:45:02', 1);

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
(64, 15, NULL, NULL, 'pre_exam', 'success', 0.829903, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:08'),
(65, 15, NULL, NULL, 'pre_exam', 'success', 0.940385, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:11'),
(66, 15, NULL, NULL, 'pre_exam', 'success', 0.903326, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:15'),
(67, 15, NULL, NULL, 'pre_exam', 'success', 0.922569, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:18'),
(68, 15, NULL, NULL, 'pre_exam', 'success', 0.915509, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:22'),
(69, 15, NULL, NULL, 'pre_exam', 'success', 0.916378, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:24'),
(70, 15, NULL, NULL, 'pre_exam', 'success', 0.920551, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:29'),
(71, 15, NULL, NULL, 'pre_exam', 'success', 0.871504, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:32'),
(72, 15, NULL, NULL, 'pre_exam', 'success', 0.888155, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:36'),
(73, 15, NULL, NULL, 'pre_exam', 'success', 0.864127, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:38'),
(74, 15, NULL, NULL, 'pre_exam', 'success', 0.925679, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:48'),
(75, 15, NULL, NULL, 'pre_exam', 'success', 0.91432, 0.8, NULL, NULL, NULL, '2026-03-31 12:43:51'),
(76, 15, NULL, NULL, 'pre_exam', 'failed', NULL, 0, 'Liveness failed: single_face', NULL, NULL, '2026-03-31 12:44:53'),
(77, 15, NULL, NULL, 'pre_exam', 'success', 0.877159, 0.8, NULL, NULL, NULL, '2026-03-31 12:44:55'),
(78, 15, 43, NULL, 'pre_exam', 'success', 0.762424, 0.8, NULL, NULL, NULL, '2026-03-31 21:25:39'),
(79, 15, 43, NULL, 'pre_exam', 'success', 0.798563, 0.8, NULL, NULL, NULL, '2026-03-31 21:25:42'),
(80, 12, 43, NULL, 'pre_exam', 'success', 0.824663, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:06'),
(81, 12, 43, NULL, 'pre_exam', 'success', 0.521434, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:09'),
(82, 12, 43, NULL, 'pre_exam', 'success', 0.505668, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:12'),
(83, 12, 43, NULL, 'pre_exam', 'success', 0.585748, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:15'),
(84, 12, 43, NULL, 'pre_exam', 'success', 0.567657, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:18'),
(85, 12, 43, NULL, 'pre_exam', 'success', 0.536231, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:24'),
(86, 12, 43, NULL, 'pre_exam', 'success', 0.573352, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:27'),
(87, 12, 43, NULL, 'pre_exam', 'success', 0.607779, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:29'),
(88, 12, 43, NULL, 'pre_exam', 'success', 0.658193, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:32'),
(89, 12, 43, NULL, 'pre_exam', 'success', 0.633193, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:35'),
(90, 12, 43, NULL, 'pre_exam', 'success', 0.62649, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:39'),
(91, 12, 43, NULL, 'pre_exam', 'success', 0.653894, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:42'),
(92, 12, 43, NULL, 'pre_exam', 'success', 0.652974, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:45'),
(93, 12, 43, NULL, 'pre_exam', 'success', 0.656879, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:47'),
(94, 12, 43, NULL, 'pre_exam', 'success', 0.609524, 0.8, NULL, NULL, NULL, '2026-03-31 22:06:50'),
(95, 12, 43, NULL, 'pre_exam', 'failed', NULL, 0, 'Liveness failed: face_present', NULL, NULL, '2026-03-31 22:06:57'),
(96, 12, 43, NULL, 'pre_exam', 'failed', NULL, 0, 'Liveness failed: single_face', NULL, NULL, '2026-03-31 22:07:00'),
(97, 12, 43, NULL, 'pre_exam', 'success', 0.514322, 0.8, NULL, NULL, NULL, '2026-03-31 22:07:03'),
(98, 12, 43, NULL, 'pre_exam', 'failed', 0.487902, 0.8, 'Low confidence: 0.49', NULL, NULL, '2026-03-31 22:07:06'),
(99, 12, 43, NULL, 'pre_exam', 'failed', 0.45601, 0.8, 'Low confidence: 0.46', NULL, NULL, '2026-03-31 22:07:09'),
(100, 12, 43, NULL, 'pre_exam', 'success', 0.747844, 0.8, NULL, NULL, NULL, '2026-03-31 22:07:13'),
(101, 12, 43, NULL, 'pre_exam', 'success', 0.64588, 0.8, NULL, NULL, NULL, '2026-03-31 22:07:16'),
(102, 12, 43, NULL, 'pre_exam', 'success', 0.574796, 0.8, NULL, NULL, NULL, '2026-03-31 22:07:19'),
(103, 12, 43, NULL, 'pre_exam', 'failed', NULL, 0, 'Liveness failed: face_present', NULL, NULL, '2026-03-31 22:07:21'),
(104, 12, 43, NULL, 'pre_exam', 'failed', NULL, 0, 'Liveness failed: single_face', NULL, NULL, '2026-03-31 22:07:24');

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
(10, 14, 14, 100, 300, '2026-03-31 07:36:36', 1, 1, '2026-03-31 07:13:52', 1, 1),
(11, 15, 10, 100, 15, '2026-03-31 12:37:57', 1, 1, '2026-03-31 12:37:42', 1, 1);

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
(350, 43, 'Describe data.', 'short_answer', 'null', 'Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.', 3, 'understand', 0, 'Reference: Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.'),
(351, 43, 'Describe education.', 'short_answer', 'null', 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 3, 'understand', 1, 'Reference: From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(352, 43, 'Fill in the blank: Machine learnin g _____ can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.', 'mcq', '[\"education\", \"learning\", \"world\", \"algorithms\"]', '3', 3, 'understand', 2, 'Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.'),
(353, 43, 'Fill in the blank: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \n_____.', 'mcq', '[\"algorithms\", \"education\", \"world\", \"learning\"]', '2', 3, 'understand', 3, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(354, 43, 'Fill in the blank: As a result, _____ is becoming more inclusive, flexible, and responsive to individual \nneeds.', 'mcq', '[\"world\", \"education\", \"learning\", \"algorithms\"]', '2', 3, 'understand', 4, 'As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.'),
(355, 43, 'Fill in the blank: Adaptive _____ platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention.', 'mcq', '[\"world\", \"learning\", \"education\", \"algorithms\"]', '1', 3, 'understand', 5, 'Adaptive learning platforms can identify a student’s strengths and weaknesses, offering tailored \ncontent that improves understanding and retention.'),
(356, 43, 'Fill in the blank: In the field of education, AI is personalizing _____ experiences for students across the globe.', 'mcq', '[\"world\", \"learning\", \"education\", \"algorithms\"]', '1', 3, 'understand', 6, 'In the field of education, AI is personalizing learning experiences for students across the globe.'),
(357, 43, 'Describe algorithms.', 'short_answer', 'null', 'Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.', 3, 'understand', 7, 'Reference: Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.'),
(358, 43, 'Fill in the blank: Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where _____al resources are \nlimited.', 'mcq', '[\"world\", \"education\", \"algorithms\", \"learning\"]', '1', 3, 'understand', 8, 'Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where educational resources are \nlimited.'),
(359, 43, 'Fill in the blank: Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \n_____ of repetitive tasks.', 'mcq', '[\"education\", \"world\", \"automation\", \"learning\"]', '2', 3, 'understand', 9, 'Companies are \nleveraging AI for customer service through chatbots, predictive analytics for market trends, and \nautomation of repetitive tasks.'),
(360, 44, 'Explain education in your own words.', 'short_answer', 'null', 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 3, 'understand', 0, 'Reference: From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(361, 44, 'Describe world.', 'short_answer', 'null', 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.', 3, 'understand', 1, 'Reference: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(362, 44, 'Fill in the blank: Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \n_____.', 'mcq', '[\"algorithms\", \"education\", \"world\", \"learning\"]', '2', 3, 'understand', 2, 'Artificial intelligence has rapidly become one of the most transformative forces shaping today’s \nworld.'),
(363, 44, 'Fill in the blank: As a result, _____ is becoming more inclusive, flexible, and responsive to individual \nneeds.', 'mcq', '[\"world\", \"learning\", \"algorithms\", \"education\"]', '1', 3, 'understand', 3, 'As a result, learning is becoming more inclusive, flexible, and responsive to individual \nneeds.'),
(364, 44, 'Summarize the concept of learning.', 'short_answer', 'null', 'In the field of education, AI is personalizing learning experiences for students across the globe.', 3, 'understand', 4, 'Reference: In the field of education, AI is personalizing learning experiences for students across the globe.'),
(365, 44, 'Fill in the blank: From healthcare to _____, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.', 'mcq', '[\"algorithms\", \"world\", \"education\", \"learning\"]', '2', 3, 'understand', 5, 'From healthcare to education, AI -driven tools are improving efficiency, accuracy, and \naccessibility in ways that were once unimaginable.'),
(366, 44, 'Fill in the blank: The business _____ is also experiencing a major shift due to AI innovation.', 'mcq', '[\"world\", \"algorithms\", \"education\", \"learning\"]', '0', 3, 'understand', 6, 'The business world is also experiencing a major shift due to AI innovation.'),
(367, 44, 'What is the significance of algorithms?', 'short_answer', 'null', 'Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.', 3, 'understand', 7, 'Reference: Machine learnin g algorithms can now \nanalyze vast amounts of data in seconds, helping doctors detect diseases earlier and enabling \nbusinesses to make smarter decisions.'),
(368, 44, 'Fill in the blank: This wave of _____ is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.', 'mcq', '[\"world\", \"learning\", \"education\", \"innovation\"]', '3', 3, 'understand', 8, 'This wave of innovation is not just about automation —\nit’s about enhancing human potential and redefinin g how we approach complex problems.'),
(369, 44, 'Fill in the blank: Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where _____al resources are \nlimited.', 'mcq', '[\"world\", \"algorithms\", \"education\", \"learning\"]', '2', 3, 'understand', 9, 'Virtual t utors and AI -powered assistants \nare making knowledge more accessible, especially in regions where educational resources are \nlimited.');

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
  `face_verified_at` datetime DEFAULT NULL,
  `grades_released` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `submissions`
--

INSERT INTO `submissions` (`id`, `exam_id`, `student_id`, `started_at`, `submitted_at`, `total_score`, `is_graded`, `is_flagged`, `risk_score`, `status`, `face_verified`, `approval_status`, `face_verified_at`, `grades_released`) VALUES
(36, 43, 15, '2026-03-31 22:35:48', '2026-03-31 22:36:39', 15, 1, 0, 30, 'submitted', 0, 'pending', NULL, 0),
(37, 44, 15, '2026-03-31 22:47:07', '2026-03-31 22:47:52', 18, 1, 0, 15, 'submitted', 0, 'pending', NULL, 1);

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
  `share_contact` tinyint(1) DEFAULT 0,
  `email_verified` tinyint(1) NOT NULL DEFAULT 1,
  `email_verification_token` varchar(100) DEFAULT NULL,
  `email_verification_token_expires` datetime DEFAULT NULL
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
(14, 'student@gmail.com', '$2b$12$S81MD6168BT28Y.pvHDzbu6tgDfdR7cDVeo0I/1Oni69r.Fy6qQDG', 'student', 'student ', 'student', 'Biology', 'profiles/_4aea87bd.jpg', 0x8004958c040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b0074946289420004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000d13bc63900000000c96d473a6151163aa719083b18a5f73a147ac83ae1ff213be0afdf3a9ddd5e3b276ab43bcd7bd33ba2d9a13b7c51063ca72a123ca3ca2d3c93221f3cdf5c4d3cc01a513cc5c18b3c892d8c3c2cf5d93ca5dcba3c7f56f43c5347e33cdbd41d3d45be1e3d6312363de528393dc59c6c3dd094563dc0a79b3d0a288a3d4cb8a43d2542ae3d8f4ad13d88b1cf3d7df8ee3d358e013e0cc2033eff9b0c3e5f29123ef9b1123ec94b1b3e9fe90f3e1c7b193ea93f143eabaf2e3e4c681b3e73ba2a3e5379273e2b882d3ef84b2e3e9bbd343e118e1f3eafaf2e3ea5a2263ecb3d313e27e0203efd01333ee5092f3e914f303ec4291d3e74ef2e3e92bb1d3e55c4283e2902113e3fb0103e90a1fb3d4d08013ee3b8f13daf7d003ef3d2cd3d1703da3da03cc23de981af3dac3f963d9357943dd39d8f3dca3e8e3d3029753dfdc26c3d850e533d1b4b553dcfb13a3de12d453db87b243d56992a3d3d9ff73c2c770e3d40a0f23c9d47043d587bf73ce14bf13c8859e03c9499093d7d03da3ca3ffea3c5803d83c8999de3cb3bdba3cfc89cb3c8830bb3c0b50ca3ccc2ec43c34eed93ce146b63c687ec53ce072c73cf335d43cb4f5d33c8dc5d93c4d9dcb3ccbf1ec3cc6b4a63cef94d83c47dfc23ce580d53c275bb93cc9fed13c8388b13ce868e33c6986a33cf482a03cfa6aa03c13dca93c3b219a3c0feaa73c4d3aa53c4137c13c4ab6853cfbfaa13ca6998d3cc51b7f3c43a59b3c8f64c73c68cf903c590cc13cdbcd6c3ce370a33cc177a93c13dca93c3354663ccb6c6f3c4664843cfb8d4a3ced42473c80766f3cb3c5593ca32c443cb9f1463c6dd6533cd02f373c5c9a593ca0fff23b8011763c9e7c1b3c3d8f373c86a8243c8f844a3c3afa083c388a533c54f5083cdb332e3c0f12093c63ba373c056b283ca345313c75c3023cf435443ce8a6123ce015313c13dcec3b20a4083cd603093c737b2e3c1f3dff3be5da0e3c1ffdf83b53122e3c13f40b3c1b7a313cdd61cd3b5750ff3b3cd5053c958fec3beb10f23b8d940b3c2b50df3b1f25da3b1f25da3beb6ee03b835be03bb097ba3bbb47c73b104ed43bec46ff3b65f6f23be474cd3b1812da3bd140c13b53c2e63b5f4ca23b855ff33beb96c13b4f66a83bb1ce8f3b3994473b48ba473b95ad543b9178af3a7c71893b3958773ac7b8153bb892953ad5de953aad21c73a7dfaad3ae352483a80fdf83ac96d473a00000000096dae3a0d70f93aa8ba473a4dd3943a496c953a2466083bec20ae3a752caf3a95dfae3a003b7b3a0dd4ad3a90d5c639f994e03a99e2f93a496c153a947494622e, 1, '2026-03-30 22:39:49', '2026-03-31 08:18:13', '0746075436', 'the best', NULL, NULL, 0),
(15, 'ever@gmail.com', '$2b$12$sbEgKYaTmwhZnmKcZqIUvOAYSPVcDOjUoNdS/wsYk51dKEK/3hnlm', 'Ever', 'Ever', 'student', 'Information Technology', 'profiles/_a997e23b.jpg', 0x8004958c040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014d0001859468038c0564747970659493948c02663494898887945294284b038c013c944e4e4e4affffffff4affffffff4b007494628942000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a4fb413ad9ed813ad9ed013a05a1423ad9ed013ab9f9a13a5053c23ac3dee33af9cb013b57f0013b3579323b3f83013b5743633b28f7523bc4f8913b1ea5813bdd4fb23bae48a23ba1f9153c53cbd23b6732e33b1d8dba3bf9cb013c33a6da3bb3241e3cd552ba3b0f5a3a3c62bd093ce52f223c3ff9193ccfae523cad5f7b3c17245f3c9700633c1470ef3cb5cb4e3c1a209a3c91782d3dcdb8c43c833ef13cdbbe403d5b31f73cb90f1a3d41aa473db17f3c3dbb32223d13cf863dd8f05d3d63687e3d1f9e9c3d70079c3df5608d3d9c09bc3d1c19a23d1c38c73d6092ba3d3c2aee3d29beca3d6f86e03dcfc4d03ddf0be43db536c93d3f89e23dc455d53d8b17e13dd080df3d2c5ef83d8f55d03d6541e83df82ce53dd845eb3d1b7d023e785dfa3df0c0f63d0a0c033e5585013e4011053e0bd8f73dd96c0f3e7058f93d5c41043ebdbaeb3d5987043efca6e63d0a82053ee164f83d3901023e480fdf3d6508053ec59ced3dabd2f73dad65d83ddbaeee3dd1e0d63d5cdcd83d0b36c73d4d15e73d7d5ad23d9bdcd93de463b53d2554d63d6d55b03da51fc53da776ae3dcb2cc93d60eaaa3da425c43da58ebe3de8c2c43d7d5aa83d611fa23d6e0c983d62788f3d30688c3de174903dd5e78a3d5486973d2866883dc1a5a03d59f7913d4ab9823d5ff6913db1e48e3d6881983dcfafa13d23d88b3de16a933d435e893d17ce883de631823dcd86953da8727e3d9173913d4c52863de430803d6991473df537773d4be9583dadee583def045d3d54f4603d713b6a3d83f4623db490433d20dc583d30c7513dcd27683dd57d373d9bc94a3d90b3473d15d2513da576363d63d04c3d13061a3db0ec4b3d7319153db56d2b3d396c273dd8b93f3de419133d9f76333d27f00d3d11b5373d85fb463df86c343d79de0b3d2b18533da60b193db7a7433d12fa123da8b2493d256c393d5bb1483dbb44f33c2b39253dd33ef13c8e131a3d9bd2d63cea51263dd023a43c2d231d3d2da4ca3c9434e53c7365bc3ccb1ffb3cc0c0ce3cf9aac63c5d59be3ccda9c23c01db913c8f4bb63c2cd3523cf0c3833c1d31733c185fa23c3bf1913cd10c923ce9db833c2d0d983c03fa113cb350a83c1cff953cc456633c93b1463c63f4623c69fa4e3c4114673c9bf9663c8b82363cb3b5423c53de873ca9882e3cbd156b3c377b2e3c4c62773c096a2a3c512a983c18e4113c307f323cdd92773cb7065b3c9d87423cec276b3c2cf5093c91ae4e3c5d8e3a3c05a87f3ce37ab43c887cc23c45321e3ddff70f3dd5b8463dbc56643dcbcfbe3cf0bd7f3c03306f3c947494622e, 1, '2026-03-31 12:35:16', '2026-03-31 12:41:12', '07123456767', 'very hardworking', NULL, NULL, 0);

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
  `violation_type` enum('multiple_faces','no_face','eye_gaze','head_pose','lip_movement','phone_detected','tab_switch','background_person','other','fullscreen_exit','noise_detected','window_blur','keyboard_shortcut') NOT NULL,
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
(541, 36, 'eye_gaze', 5, 'Looking away: unknown', NULL, '2026-03-31 22:36:01', 'clip_541_20260331_223609.webm', 'video/webm', 8),
(542, 36, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-31 22:36:16', NULL, NULL, NULL),
(543, 36, 'eye_gaze', 5, 'Looking away: unknown', NULL, '2026-03-31 22:36:32', 'clip_543_20260331_223640.webm', 'video/webm', 8),
(544, 36, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-31 22:36:42', NULL, NULL, NULL),
(545, 37, 'eye_gaze', 5, 'Looking away: unknown', NULL, '2026-03-31 22:47:50', 'clip_545_20260331_224752.webm', 'video/webm', 8),
(546, 37, 'tab_switch', 10, 'Student switched browser tab/window', NULL, '2026-03-31 22:47:54', NULL, NULL, NULL);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=214;

--
-- AUTO_INCREMENT for table `courses`
--
ALTER TABLE `courses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `enrollments`
--
ALTER TABLE `enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `exams`
--
ALTER TABLE `exams`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `face_admin_actions`
--
ALTER TABLE `face_admin_actions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `face_verification_logs`
--
ALTER TABLE `face_verification_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=105;

--
-- AUTO_INCREMENT for table `learning_progress`
--
ALTER TABLE `learning_progress`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=370;

--
-- AUTO_INCREMENT for table `submissions`
--
ALTER TABLE `submissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `user_analytics`
--
ALTER TABLE `user_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `violations`
--
ALTER TABLE `violations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=549;

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

-- ============================================================
-- MIGRATION: Enhanced Proctoring — run once on existing DBs
-- ============================================================

-- 1. Expand violation_type enum with new monitoring categories
ALTER TABLE `violations`
  MODIFY COLUMN `violation_type`
    ENUM(
      'multiple_faces','no_face','eye_gaze','head_pose',
      'lip_movement','phone_detected','tab_switch',
      'background_person','other',
      'fullscreen_exit','noise_detected','window_blur','keyboard_shortcut'
    ) NOT NULL;

-- ============================================================
-- MIGRATION: Email Verification — run once on existing DBs
-- ============================================================

-- 2a. Add email verification columns (existing users set to verified=1)
ALTER TABLE `users`
  ADD COLUMN IF NOT EXISTS `email_verified` tinyint(1) NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS `email_verification_token` varchar(100) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `email_verification_token_expires` datetime DEFAULT NULL;

-- 2b. Index for fast token lookups
ALTER TABLE `users`
  ADD INDEX IF NOT EXISTS `ix_users_email_verification_token` (`email_verification_token`);

-- ============================================================

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
