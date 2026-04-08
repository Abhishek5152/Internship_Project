-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 08, 2026 at 12:21 PM
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
-- Database: `db_eerm`
--

-- --------------------------------------------------------

--
-- Table structure for table `eerm_alloc`
--

CREATE TABLE `eerm_alloc` (
  `alloc_id` int(11) NOT NULL,
  `res_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `alloc_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `ret_date` timestamp NULL DEFAULT NULL,
  `alloc_status` enum('Allocated','Returned') NOT NULL DEFAULT 'Allocated'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_apr`
--

CREATE TABLE `eerm_apr` (
  `apr_id` int(11) NOT NULL,
  `exp_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `apr_status` enum('Approve','Reject') NOT NULL,
  `apr_remark` varchar(225) NOT NULL,
  `apr_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_budget`
--

CREATE TABLE `eerm_budget` (
  `budget_id` int(11) NOT NULL,
  `dept_id` int(11) NOT NULL,
  `cat_id` int(11) NOT NULL,
  `amt_lmt` decimal(12,2) NOT NULL,
  `avail_bgt` decimal(12,2) NOT NULL,
  `bgt_year` year(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_dept`
--

CREATE TABLE `eerm_dept` (
  `dept_id` int(11) NOT NULL,
  `dept_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_exp`
--

CREATE TABLE `eerm_exp` (
  `exp_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `cat_id` int(11) NOT NULL,
  `exp_amt` decimal(10,2) NOT NULL,
  `exp_desc` text NOT NULL,
  `exp_date` date NOT NULL,
  `receipt_url` varchar(500) NOT NULL,
  `exp_status` enum('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_expcat`
--

CREATE TABLE `eerm_expcat` (
  `cat_id` int(11) NOT NULL,
  `cat_name` varchar(100) NOT NULL,
  `cat_desc` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_forpass`
--

CREATE TABLE `eerm_forpass` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_logs`
--

CREATE TABLE `eerm_logs` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` varchar(150) NOT NULL,
  `entity` varchar(100) NOT NULL,
  `entity_id` int(11) NOT NULL,
  `log_desc` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_notifs`
--

CREATE TABLE `eerm_notifs` (
  `notif_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `actor_id` int(11) DEFAULT NULL,
  `notif_type` varchar(50) DEFAULT NULL,
  `message` varchar(255) NOT NULL,
  `reference_id` int(11) DEFAULT NULL,
  `reference_table` varchar(50) DEFAULT NULL,
  `priority` enum('low','normal','high','critical') DEFAULT 'normal',
  `read_at` timestamp NULL DEFAULT NULL,
  `channel` enum('in_app','email','push') DEFAULT 'in_app',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `expires_at` timestamp NULL DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_poli`
--

CREATE TABLE `eerm_poli` (
  `poli_id` int(11) NOT NULL,
  `cat_id` int(11) NOT NULL,
  `policat_id` int(11) NOT NULL,
  `rule_value` varchar(100) NOT NULL,
  `poli_desc` varchar(225) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_policat`
--

CREATE TABLE `eerm_policat` (
  `cat_id` int(11) NOT NULL,
  `cat_name` varchar(100) NOT NULL,
  `cat_desc` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_req`
--

CREATE TABLE `eerm_req` (
  `req_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `res_id` int(11) NOT NULL,
  `req_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `req_status` enum('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_res`
--

CREATE TABLE `eerm_res` (
  `res_id` int(11) NOT NULL,
  `cat_id` int(11) NOT NULL,
  `res_name` varchar(100) NOT NULL,
  `res_type` enum('Physical','Digital','Shared') NOT NULL,
  `res_desc` text NOT NULL,
  `res_status` enum('Available','Allocated','Under Maintainance') NOT NULL DEFAULT 'Available',
  `res_lifestatus` enum('Active','Retired') NOT NULL DEFAULT 'Active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_rescat`
--

CREATE TABLE `eerm_rescat` (
  `cat_id` int(11) NOT NULL,
  `cat_name` varchar(100) NOT NULL,
  `cat_desc` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `eerm_users`
--

CREATE TABLE `eerm_users` (
  `user_id` int(11) NOT NULL,
  `user_name` varchar(100) NOT NULL,
  `user_email` varchar(150) NOT NULL,
  `user_pass` varchar(255) NOT NULL,
  `user_role` enum('Employee','Manager','Admin') NOT NULL,
  `dept_id` int(11) DEFAULT NULL,
  `user_status` enum('Active','Inactive') NOT NULL DEFAULT 'Active',
  `user_contact` varchar(10) DEFAULT NULL,
  `user_address` text DEFAULT NULL,
  `user_about` text DEFAULT NULL,
  `user_img_url` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `eerm_alloc`
--
ALTER TABLE `eerm_alloc`
  ADD PRIMARY KEY (`alloc_id`),
  ADD KEY `eerm_alloc_ibfk_1` (`res_id`),
  ADD KEY `eerm_alloc_ibfk_2` (`user_id`);

--
-- Indexes for table `eerm_apr`
--
ALTER TABLE `eerm_apr`
  ADD PRIMARY KEY (`apr_id`),
  ADD KEY `eerm_apr_ibfk_1` (`exp_id`),
  ADD KEY `eerm_apr_ibfk_2` (`user_id`);

--
-- Indexes for table `eerm_budget`
--
ALTER TABLE `eerm_budget`
  ADD PRIMARY KEY (`budget_id`),
  ADD KEY `eerm_budget_ibfk_1` (`cat_id`),
  ADD KEY `eerm_budget_ibfk_2` (`dept_id`);

--
-- Indexes for table `eerm_dept`
--
ALTER TABLE `eerm_dept`
  ADD PRIMARY KEY (`dept_id`),
  ADD UNIQUE KEY `dept_name` (`dept_name`);

--
-- Indexes for table `eerm_exp`
--
ALTER TABLE `eerm_exp`
  ADD PRIMARY KEY (`exp_id`),
  ADD KEY `eerm_exp_ibfk_1` (`user_id`),
  ADD KEY `eerm_exp_ibfk_2` (`cat_id`);

--
-- Indexes for table `eerm_expcat`
--
ALTER TABLE `eerm_expcat`
  ADD PRIMARY KEY (`cat_id`);

--
-- Indexes for table `eerm_forpass`
--
ALTER TABLE `eerm_forpass`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `eerm_logs`
--
ALTER TABLE `eerm_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `eerm_logs_ibfk_1` (`user_id`);

--
-- Indexes for table `eerm_notifs`
--
ALTER TABLE `eerm_notifs`
  ADD PRIMARY KEY (`notif_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `read_at` (`read_at`),
  ADD KEY `created_at` (`created_at`);

--
-- Indexes for table `eerm_poli`
--
ALTER TABLE `eerm_poli`
  ADD PRIMARY KEY (`poli_id`),
  ADD KEY `cat_id` (`cat_id`),
  ADD KEY `policat_id` (`policat_id`);

--
-- Indexes for table `eerm_policat`
--
ALTER TABLE `eerm_policat`
  ADD PRIMARY KEY (`cat_id`);

--
-- Indexes for table `eerm_req`
--
ALTER TABLE `eerm_req`
  ADD PRIMARY KEY (`req_id`),
  ADD KEY `eerm_req_ibfk_1` (`user_id`),
  ADD KEY `eerm_req_ibfk_2` (`res_id`);

--
-- Indexes for table `eerm_res`
--
ALTER TABLE `eerm_res`
  ADD PRIMARY KEY (`res_id`),
  ADD KEY `cat_id` (`cat_id`);

--
-- Indexes for table `eerm_rescat`
--
ALTER TABLE `eerm_rescat`
  ADD PRIMARY KEY (`cat_id`);

--
-- Indexes for table `eerm_users`
--
ALTER TABLE `eerm_users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD KEY `dept_id` (`dept_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `eerm_alloc`
--
ALTER TABLE `eerm_alloc`
  MODIFY `alloc_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_apr`
--
ALTER TABLE `eerm_apr`
  MODIFY `apr_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_budget`
--
ALTER TABLE `eerm_budget`
  MODIFY `budget_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_dept`
--
ALTER TABLE `eerm_dept`
  MODIFY `dept_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_exp`
--
ALTER TABLE `eerm_exp`
  MODIFY `exp_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_expcat`
--
ALTER TABLE `eerm_expcat`
  MODIFY `cat_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_forpass`
--
ALTER TABLE `eerm_forpass`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_logs`
--
ALTER TABLE `eerm_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_notifs`
--
ALTER TABLE `eerm_notifs`
  MODIFY `notif_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_poli`
--
ALTER TABLE `eerm_poli`
  MODIFY `poli_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_policat`
--
ALTER TABLE `eerm_policat`
  MODIFY `cat_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_req`
--
ALTER TABLE `eerm_req`
  MODIFY `req_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_res`
--
ALTER TABLE `eerm_res`
  MODIFY `res_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_rescat`
--
ALTER TABLE `eerm_rescat`
  MODIFY `cat_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `eerm_users`
--
ALTER TABLE `eerm_users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `eerm_alloc`
--
ALTER TABLE `eerm_alloc`
  ADD CONSTRAINT `eerm_alloc_ibfk_1` FOREIGN KEY (`res_id`) REFERENCES `eerm_res` (`res_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_alloc_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `eerm_apr`
--
ALTER TABLE `eerm_apr`
  ADD CONSTRAINT `eerm_apr_ibfk_1` FOREIGN KEY (`exp_id`) REFERENCES `eerm_exp` (`exp_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_apr_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `eerm_budget`
--
ALTER TABLE `eerm_budget`
  ADD CONSTRAINT `eerm_budget_ibfk_1` FOREIGN KEY (`cat_id`) REFERENCES `eerm_expcat` (`cat_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_budget_ibfk_2` FOREIGN KEY (`dept_id`) REFERENCES `eerm_dept` (`dept_id`) ON UPDATE CASCADE;

--
-- Constraints for table `eerm_exp`
--
ALTER TABLE `eerm_exp`
  ADD CONSTRAINT `eerm_exp_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_exp_ibfk_2` FOREIGN KEY (`cat_id`) REFERENCES `eerm_expcat` (`cat_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `eerm_forpass`
--
ALTER TABLE `eerm_forpass`
  ADD CONSTRAINT `eerm_forpass_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`);

--
-- Constraints for table `eerm_logs`
--
ALTER TABLE `eerm_logs`
  ADD CONSTRAINT `eerm_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `eerm_notifs`
--
ALTER TABLE `eerm_notifs`
  ADD CONSTRAINT `eerm_notifs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`);

--
-- Constraints for table `eerm_poli`
--
ALTER TABLE `eerm_poli`
  ADD CONSTRAINT `eerm_poli_ibfk_1` FOREIGN KEY (`cat_id`) REFERENCES `eerm_expcat` (`cat_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_poli_ibfk_2` FOREIGN KEY (`policat_id`) REFERENCES `eerm_policat` (`cat_id`) ON UPDATE CASCADE;

--
-- Constraints for table `eerm_req`
--
ALTER TABLE `eerm_req`
  ADD CONSTRAINT `eerm_req_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `eerm_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `eerm_req_ibfk_2` FOREIGN KEY (`res_id`) REFERENCES `eerm_res` (`res_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `eerm_res`
--
ALTER TABLE `eerm_res`
  ADD CONSTRAINT `eerm_res_ibfk_1` FOREIGN KEY (`cat_id`) REFERENCES `eerm_rescat` (`cat_id`) ON UPDATE CASCADE;

--
-- Constraints for table `eerm_users`
--
ALTER TABLE `eerm_users`
  ADD CONSTRAINT `eerm_users_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `eerm_dept` (`dept_id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
