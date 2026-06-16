import sys
import os
import struct

def get_mp4_duration(file_path):
    """Parses MP4 binary structure to extract time scale and duration without external dependencies."""
    try:
        with open(file_path, 'rb') as f:
            while True:
                header = f.read(8)
                if len(header) < 8:
                    break
                size, name = struct.unpack('>I4s', header)
                if name == b'moov':
                    # The 'moov' atom is a container, look for 'mvhd' atom directly inside
                    mvhd_header = f.read(8)
                    m_size, m_name = struct.unpack('>I4s', mvhd_header)
                    if m_name == b'mvhd':
                        version = struct.unpack('>B', f.read(1))[0]
                        f.read(3)  # flags
                        if version == 1:
                            f.read(16)  # creation & modification times (8 bytes each)
                            time_scale = struct.unpack('>I', f.read(4))[0]
                            duration = struct.unpack('>Q', f.read(8))[0]
                        else:
                            f.read(8)  # creation & modification times (4 bytes each)
                            time_scale = struct.unpack('>I', f.read(4))[0]
                            duration = struct.unpack('>I', f.read(4))[0]
                        return duration / time_scale
                    else:
                        # Skip if it is not mvhd
                        f.seek(m_size - 8, 1)
                else:
                    if size == 1:
                        # 64-bit size field
                        size = struct.unpack('>Q', f.read(8))[0]
                        f.seek(size - 16, 1)
                    elif size == 0:
                        # Extends to end of file
                        break
                    else:
                        f.seek(size - 8, 1)
    except Exception as e:
        print(f"Erro ao analisar o arquivo MP4: {e}")
    return None

def format_duration(seconds):
    """Formats raw seconds into the requested XhYmZs format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    
    return "".join(parts)

def main():
    if len(sys.argv) < 2:
        print("Uso: python get_video_duration.py [caminho_do_video.mp4]")
        return
        
    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Erro: O arquivo '{video_path}' não foi encontrado.")
        return
        
    seconds = get_mp4_duration(video_path)
    if seconds is not None:
        formatted = format_duration(seconds)
        print(f"Duração extraída: {formatted} (total de {seconds:.2f} segundos)")
    else:
        print("Erro: Não foi possível extrair a duração do arquivo de vídeo.")

if __name__ == "__main__":
    main()
