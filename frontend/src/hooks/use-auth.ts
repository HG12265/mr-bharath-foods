import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import authService from "../services/auth-service";

export const useRegister = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => authService.register(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => authService.login(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useRequestOtp = () => {
  return useMutation({
    mutationFn: (payload: any) => authService.requestOtp(payload),
  });
};

export const useVerifyOtp = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => authService.verifyOtp(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      queryClient.clear();
    },
  });
};

export const useMe = (options?: { enabled?: boolean; staleTime?: number }) => {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => authService.getMe(),
    retry: false,
    ...options,
  });
};
