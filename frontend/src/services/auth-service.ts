import { apiClient, setAccessToken } from "./api-client";
import { Envelope, Token, User } from "../types";

export const authService = {
  async register(payload: any): Promise<Envelope<User>> {
    const response = await apiClient.post<Envelope<User>>("/api/v1/auth/register", payload);
    return response.data;
  },

  async login(payload: any): Promise<Envelope<Token>> {
    const response = await apiClient.post<Envelope<Token>>("/api/v1/auth/login", payload);
    setAccessToken(response.data.data.access_token);
    return response.data;
  },

  async requestOtp(payload: any): Promise<Envelope<null>> {
    const response = await apiClient.post<Envelope<null>>("/api/v1/auth/otp/request", payload);
    return response.data;
  },

  async verifyOtp(payload: any): Promise<Envelope<Token>> {
    const response = await apiClient.post<Envelope<Token>>("/api/v1/auth/otp/verify", payload);
    setAccessToken(response.data.data.access_token);
    return response.data;
  },

  async logout(): Promise<Envelope<null>> {
    const response = await apiClient.post<Envelope<null>>("/api/v1/auth/logout");
    setAccessToken(null);
    return response.data;
  },

  async getMe(): Promise<Envelope<User>> {
    const response = await apiClient.get<Envelope<User>>("/api/v1/auth/me");
    return response.data;
  },
};
export default authService;
