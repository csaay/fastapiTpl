import { useState, useRef, useCallback } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { Upload, Crop, Copy, Check, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { OpenAPI } from "@/client"

export const Route = createFileRoute("/_layout/sim-ocr")({
    component: SimOcrPage,
    head: () => ({
        meta: [{ title: "SIM卡号识别 - FastAPI Cloud" }],
    }),
})

interface CropArea {
    startX: number
    startY: number
    endX: number
    endY: number
}

function SimOcrPage() {
    const [image, setImage] = useState<string | null>(null)
    const [cropArea, setCropArea] = useState<CropArea | null>(null)
    const [isDragging, setIsDragging] = useState(false)
    const [simNumber, setSimNumber] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [copied, setCopied] = useState(false)

    const canvasRef = useRef<HTMLCanvasElement>(null)
    const imageRef = useRef<HTMLImageElement | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const dragStartRef = useRef<{ x: number; y: number } | null>(null)

    // 处理文件上传
    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        if (!file.type.startsWith("image/")) {
            toast.error("请上传图片文件")
            return
        }

        const reader = new FileReader()
        reader.onload = (event) => {
            const img = new Image()
            img.onload = () => {
                imageRef.current = img
                setImage(event.target?.result as string)
                setCropArea(null)
                setSimNumber(null)
                drawImage(img)
            }
            img.src = event.target?.result as string
        }
        reader.readAsDataURL(file)
    }, [])

    // 绘制图片到 canvas
    const drawImage = useCallback((img: HTMLImageElement, crop?: CropArea) => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext("2d")
        if (!ctx) return

        // 设置 canvas 尺寸
        const maxWidth = 800
        const maxHeight = 600
        let { width, height } = img

        if (width > maxWidth) {
            height = (height * maxWidth) / width
            width = maxWidth
        }
        if (height > maxHeight) {
            width = (width * maxHeight) / height
            height = maxHeight
        }

        canvas.width = width
        canvas.height = height

        ctx.drawImage(img, 0, 0, width, height)

        // 绘制裁剪区域
        if (crop) {
            ctx.strokeStyle = "#3b82f6"
            ctx.lineWidth = 2
            ctx.setLineDash([5, 5])
            ctx.strokeRect(
                Math.min(crop.startX, crop.endX),
                Math.min(crop.startY, crop.endY),
                Math.abs(crop.endX - crop.startX),
                Math.abs(crop.endY - crop.startY)
            )

            // 半透明遮罩
            ctx.fillStyle = "rgba(0, 0, 0, 0.3)"
            ctx.fillRect(0, 0, canvas.width, canvas.height)

            // 清除选中区域的遮罩
            ctx.clearRect(
                Math.min(crop.startX, crop.endX),
                Math.min(crop.startY, crop.endY),
                Math.abs(crop.endX - crop.startX),
                Math.abs(crop.endY - crop.startY)
            )
            ctx.drawImage(
                img,
                (Math.min(crop.startX, crop.endX) / canvas.width) * img.width,
                (Math.min(crop.startY, crop.endY) / canvas.height) * img.height,
                (Math.abs(crop.endX - crop.startX) / canvas.width) * img.width,
                (Math.abs(crop.endY - crop.startY) / canvas.height) * img.height,
                Math.min(crop.startX, crop.endX),
                Math.min(crop.startY, crop.endY),
                Math.abs(crop.endX - crop.startX),
                Math.abs(crop.endY - crop.startY)
            )
        }
    }, [])

    // 鼠标事件处理
    const getMousePos = (e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current
        if (!canvas) return { x: 0, y: 0 }
        const rect = canvas.getBoundingClientRect()
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        }
    }

    const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
        const pos = getMousePos(e)
        dragStartRef.current = pos
        setIsDragging(true)
        setCropArea({ startX: pos.x, startY: pos.y, endX: pos.x, endY: pos.y })
    }

    const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
        if (!isDragging || !dragStartRef.current || !imageRef.current) return

        const pos = getMousePos(e)
        const newCrop = {
            startX: dragStartRef.current.x,
            startY: dragStartRef.current.y,
            endX: pos.x,
            endY: pos.y,
        }
        setCropArea(newCrop)
        drawImage(imageRef.current, newCrop)
    }

    const handleMouseUp = () => {
        setIsDragging(false)
    }

    // 裁剪并上传
    const handleRecognize = async () => {
        if (!imageRef.current || !cropArea || !canvasRef.current) {
            toast.error("请先选择要识别的区域")
            return
        }

        setIsLoading(true)

        try {
            // 创建裁剪后的图片
            const cropCanvas = document.createElement("canvas")
            const cropCtx = cropCanvas.getContext("2d")
            if (!cropCtx) throw new Error("无法创建 canvas context")

            const img = imageRef.current
            const canvas = canvasRef.current

            // 计算实际裁剪区域（相对于原始图片）
            const scaleX = img.width / canvas.width
            const scaleY = img.height / canvas.height

            const cropX = Math.min(cropArea.startX, cropArea.endX) * scaleX
            const cropY = Math.min(cropArea.startY, cropArea.endY) * scaleY
            const cropW = Math.abs(cropArea.endX - cropArea.startX) * scaleX
            const cropH = Math.abs(cropArea.endY - cropArea.startY) * scaleY

            cropCanvas.width = cropW
            cropCanvas.height = cropH
            cropCtx.drawImage(img, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH)

            // 转换为 Blob
            const blob = await new Promise<Blob>((resolve, reject) => {
                cropCanvas.toBlob((b) => {
                    if (b) resolve(b)
                    else reject(new Error("无法转换图片"))
                }, "image/png")
            })

            // 上传到 OCR 接口（使用 OpenAPI.BASE 配置的地址）
            const formData = new FormData()
            formData.append("file", blob, "cropped.png")

            const token = localStorage.getItem("access_token")
            const response = await fetch(`${OpenAPI.BASE}/api/v1/ocr/recognize`, {
                method: "POST",
                headers: token ? { Authorization: `Bearer ${token}` } : {},
                body: formData,
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.message || "识别失败")
            }

            const result = await response.json()

            if (result.code === 200 && result.data?.sim_number) {
                setSimNumber(result.data.sim_number)
                toast.success("识别成功！")
            } else {
                toast.error(result.message || "未识别到 SIM 卡号")
            }
        } catch (error) {
            console.error(error)
            toast.error(error instanceof Error ? error.message : "识别失败")
        } finally {
            setIsLoading(false)
        }
    }

    // 复制到剪贴板
    const handleCopy = () => {
        if (!simNumber) return
        navigator.clipboard.writeText(simNumber)
        setCopied(true)
        toast.success("已复制到剪贴板")
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">SIM 卡号识别</h1>
                <p className="text-muted-foreground">
                    上传 SIM 卡图片，框选卡号区域，自动识别卡号
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* 左侧：上传和框选 */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Crop className="h-5 w-5" />
                            选择识别区域
                        </CardTitle>
                        <CardDescription>
                            上传图片后，用鼠标框选包含卡号的区域
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className="hidden"
                        />

                        <Button
                            variant="outline"
                            className="w-full"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Upload className="mr-2 h-4 w-4" />
                            上传图片
                        </Button>

                        {image ? (
                            <div className="relative border rounded-lg overflow-hidden bg-muted">
                                <canvas
                                    ref={canvasRef}
                                    className="cursor-crosshair max-w-full"
                                    onMouseDown={handleMouseDown}
                                    onMouseMove={handleMouseMove}
                                    onMouseUp={handleMouseUp}
                                    onMouseLeave={handleMouseUp}
                                />
                            </div>
                        ) : (
                            <div className="border-2 border-dashed rounded-lg p-12 text-center text-muted-foreground">
                                <Upload className="mx-auto h-12 w-12 mb-4 opacity-50" />
                                <p>点击上方按钮上传 SIM 卡图片</p>
                            </div>
                        )}

                        <Button
                            className="w-full"
                            onClick={handleRecognize}
                            disabled={!cropArea || isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    识别中...
                                </>
                            ) : (
                                "开始识别"
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* 右侧：识别结果 */}
                <Card>
                    <CardHeader>
                        <CardTitle>识别结果</CardTitle>
                        <CardDescription>
                            识别出的 SIM 卡号将显示在下方
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {simNumber ? (
                            <div className="space-y-4">
                                <div className="p-6 bg-muted rounded-lg">
                                    <p className="text-xs text-muted-foreground mb-2">SIM 卡号</p>
                                    <p className="text-2xl font-mono font-bold tracking-wider break-all">
                                        {simNumber}
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    className="w-full"
                                    onClick={handleCopy}
                                >
                                    {copied ? (
                                        <>
                                            <Check className="mr-2 h-4 w-4 text-green-500" />
                                            已复制
                                        </>
                                    ) : (
                                        <>
                                            <Copy className="mr-2 h-4 w-4" />
                                            复制卡号
                                        </>
                                    )}
                                </Button>
                            </div>
                        ) : (
                            <div className="text-center text-muted-foreground py-12">
                                <p>请先上传图片并框选区域进行识别</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
