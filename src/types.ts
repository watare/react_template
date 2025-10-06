// User type for authentication
export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

// Dashboard data type
export interface DashboardData {
  totalUsers: number;
  activeProjects: number;
  completedTasks: number;
  recentActivity: Activity[];
}

// Activity type for recent activities
export interface Activity {
  id: string;
  user: string;
  action: string;
  timestamp: Date;
}
