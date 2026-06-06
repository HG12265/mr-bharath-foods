import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import notificationService, { ListNotificationsParams } from "../services/notification-service";

export const useNotifications = (params?: ListNotificationsParams) => {
  return useQuery({
    queryKey: ["notifications", params],
    queryFn: () => notificationService.listMyNotifications(params),
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationService.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useAdminNotifications = (params?: ListNotificationsParams) => {
  return useQuery({
    queryKey: ["admin", "notifications", params],
    queryFn: () => notificationService.adminListNotifications(params),
  });
};
