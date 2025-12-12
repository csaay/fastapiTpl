import { AxiosError } from "axios"
import type { ApiError } from "./client"

function extractErrorMessage(err: ApiError): string {
  if (err instanceof AxiosError) {
    return err.message
  }

  const body = err.body as Record<string, unknown> | undefined
  
  // 新的统一响应格式: { code, message, data }
  if (body?.message && typeof body.message === "string") {
    return body.message
  }
  
  // 旧的 FastAPI 验证错误格式: { detail: [...] } 或 { detail: "..." }
  const errDetail = body?.detail
  if (Array.isArray(errDetail) && errDetail.length > 0) {
    return errDetail[0].msg
  }
  if (typeof errDetail === "string") {
    return errDetail
  }
  
  return "Something went wrong."
}

export const handleError = function (
  this: (msg: string) => void,
  err: ApiError,
) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
