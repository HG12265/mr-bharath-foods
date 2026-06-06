import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url().default("http://localhost:8000"),
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

const getEnvData = () => {
  return {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
    NODE_ENV: process.env.NODE_ENV || "development",
  };
};

const parseEnv = () => {
  const envData = getEnvData();
  const result = envSchema.safeParse(envData);

  if (!result.success) {
    console.error("❌ Invalid environment variables configuration:", result.error.format());
    if (process.env.NODE_ENV === "production") {
      throw new Error("Missing or invalid crucial environment variables. Build aborted.");
    }
    // Return safe default fallbacks for local development compiling
    return {
      NEXT_PUBLIC_API_URL: "http://localhost:8000",
      NEXT_PUBLIC_APP_URL: "http://localhost:3000",
      NODE_ENV: "development" as const,
    };
  }

  return result.data;
};

export const env = parseEnv();
export type Env = z.infer<typeof envSchema>;
