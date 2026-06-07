import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import inventoryService, { StockAdjustmentPayload } from "../services/inventory-service";

export const useInventoryBySku = (sku: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ["inventory", sku],
    queryFn: () => inventoryService.getInventoryBySku(sku),
    enabled: options?.enabled !== undefined ? options.enabled && !!sku : !!sku,
  });
};

export const useAdjustStock = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sku, payload }: { sku: string; payload: StockAdjustmentPayload }) =>
      inventoryService.adjustStock(sku, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["inventory", variables.sku] });
      queryClient.invalidateQueries({ queryKey: ["admin", "dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
};
