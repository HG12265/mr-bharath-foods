import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import authService from "../services/auth-service";
import { setSessionAuthenticated, setRefreshFailed } from "../services/api-client";

export const useRegister = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => authService.register(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["session"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => authService.login(payload),
    onSuccess: () => {
      if (typeof window !== "undefined") {
        localStorage.setItem("was_logged_in", "true");
      }
      setSessionAuthenticated(true);
      setRefreshFailed(false);
      queryClient.invalidateQueries({ queryKey: ["session"] });
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
      if (typeof window !== "undefined") {
        localStorage.setItem("was_logged_in", "true");
      }
      setSessionAuthenticated(true);
      setRefreshFailed(false);
      queryClient.invalidateQueries({ queryKey: ["session"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      if (typeof window !== "undefined") {
        localStorage.removeItem("was_logged_in");
      }
      setSessionAuthenticated(false);
      queryClient.clear();
    },
  });
};

export const useMe = (options?: { enabled?: boolean; staleTime?: number }) => {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => authService.getMe(),
    retry: false,
    refetchOnWindowFocus: false,
    ...options,
  });
};

export const useSession = (options?: { enabled?: boolean; staleTime?: number }) => {
  return useQuery({
    queryKey: ["session"],
    queryFn: () => authService.getSession(),
    retry: false,
    refetchOnWindowFocus: false,
    ...options,
  });
};
