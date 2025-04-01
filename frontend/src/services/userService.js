const API_URL = 'http://localhost:5005/api/users';

export const userService = {
  async registerUser(username, email) {
    try {
      const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return {
        user_id: data.user_id,
        username: data.username,
        email: data.email
      };
    } catch (error) {
      console.error('Error registering user:', error);
      throw error;
    }
  },

  async getUser(userId) {
    try {
      const response = await fetch(`${API_URL}/${userId}`);
      
      if (response.status === 404) {
        throw new Error('USER_NOT_FOUND');
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return {
        user_id: data.user_id,
        username: data.username,
        email: data.email
      };
    } catch (error) {
      console.error('Error getting user:', error);
      throw error;
    }
  },

  async searchUsers(query) {
    try {
      const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error searching users:', error);
      throw error;
    }
  },

  async getUserByEmail(email) {
    try {
      const users = await this.searchUsers(email);
      const user = users.find(u => u.email === email);
      if (!user) {
        throw new Error('USER_NOT_FOUND');
      }
      return user;
    } catch (error) {
      console.error('Error getting user by email:', error);
      throw error;
    }
  }
}; 