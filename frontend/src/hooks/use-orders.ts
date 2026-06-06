import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import orderService, { ListOrdersParams, AdminUpdateOrderStatusPayload } from "../services/order-service";

export const useCreateOrderFromCheckout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (checkoutId: string) => orderService.createOrderFromCheckout(checkoutId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });
};

export const useOrders = (params?: ListOrdersParams) => {
  return useQuery({
    queryKey: ["orders", params],
    queryFn: () => orderService.listOrders(params),
  });
};

export const useOrderDetails = (orderId: string) => {
  return useQuery({
    queryKey: ["order", orderId],
    queryFn: () => orderService.getOrderDetails(orderId),
    enabled: !!orderId,
  });
};

export const useCancelOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderId: string) => orderService.cancelOrder(orderId),
    onSuccess: (_, orderId) => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
    },
  });
};

export const useAdminOrders = (params?: ListOrdersParams) => {
  return useQuery({
    queryKey: ["admin", "orders", params],
    queryFn: () => orderService.adminListOrders(params),
  });
};

export const useAdminUpdateOrderStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, payload }: { orderId: string; payload: AdminUpdateOrderStatusPayload }) =>
      orderService.adminUpdateOrderStatus(orderId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["order", variables.orderId] });
      queryClient.invalidateQueries({ queryKey: ["admin", "orders"] });
    },
  });
};
