import os
import sys

def merge_obj_files_in_memory(input_directory, output_file="merged_output.obj"):
    """
    Merges all .obj files in `input_directory` into a single .obj,
    ensuring each file is written as a separate object/group so that
    Unity (or other 3D tools) can (hopefully) split them into multiple
    sub-objects on import.

    Note: Wavefront OBJ has no pivot or transform concept, so each mesh's
    vertices must already be in the correct location if you want them
    spread out (not overlapped at the origin).
    """

    obj_files = [
        f for f in os.listdir(input_directory)
        if f.lower().endswith(".obj") and os.path.isfile(os.path.join(input_directory, f))
    ]
    obj_files.sort()

    # These track how many of each kind of data we've already written
    vertex_offset = 0
    tex_offset = 0
    norm_offset = 0

    with open(output_file, 'w') as out_f:
        out_f.write("# Merged OBJ file\n\n")

        for filename in obj_files:
            filepath = os.path.join(input_directory, filename)
            obj_name = os.path.splitext(filename)[0]

            # Temporary buffers
            vertices = []
            texcoords = []
            normals = []
            faces = []

            # -- Pass 1: read data into buffers --
            with open(filepath, 'r') as in_f:
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue

                    # Ignore object/group statements from the source
                    if line.startswith('o ') or line.startswith('g '):
                        continue

                    if line.startswith('v '):
                        # e.g. "v x y z"
                        vertices.append(line)
                    elif line.startswith('vt '):
                        # e.g. "vt u v [w]"
                        texcoords.append(line)
                    elif line.startswith('vn '):
                        # e.g. "vn x y z"
                        normals.append(line)
                    elif line.startswith('f '):
                        # e.g. "f v/vt/vn v/vt/vn v/vt/vn ..."
                        faces.append(line)
                    else:
                        pass

            # -- Write new object & group statements --
            out_f.write(f"o {obj_name}\n")
            out_f.write(f"g {obj_name}\n")

            # -- Pass 2: Write vertices, texcoords, normals exactly as is --
            for v in vertices:
                out_f.write(v + "\n")
            for vt in texcoords:
                out_f.write(vt + "\n")
            for vn in normals:
                out_f.write(vn + "\n")

            # -- Pass 3: Fix faces with offsets and write them --
            for face_line in faces:
                parts = face_line.split()[1:]  # skip 'f'
                new_face_tokens = []
                for p in parts:
                    # p might be "v", "v/t", or "v/t/n"
                    indices = p.split('/')

                    # Vertex index
                    if len(indices) > 0 and indices[0]:
                        v_idx = int(indices[0]) + vertex_offset
                    else:
                        v_idx = ""

                    # Texture index
                    if len(indices) > 1 and indices[1]:
                        t_idx = int(indices[1]) + tex_offset
                    else:
                        t_idx = ""

                    # Normal index
                    if len(indices) > 2 and indices[2]:
                        n_idx = int(indices[2]) + norm_offset
                    else:
                        n_idx = ""

                    # Rebuild the face token
                    if t_idx == "" and n_idx == "":
                        new_face_tokens.append(f"{v_idx}")
                    elif n_idx == "":
                        new_face_tokens.append(f"{v_idx}/{t_idx}")
                    else:
                        new_face_tokens.append(f"{v_idx}/{t_idx}/{n_idx}")

                out_f.write("f " + " ".join(new_face_tokens) + "\n")

            # -- Update offsets for the next file --
            vertex_offset += len(vertices)
            tex_offset += len(texcoords)
            norm_offset += len(normals)


if __name__ == "__main__":
    """
    Usage: python merge_obj.py path/to/directory merged_output.obj

    If only one argument is given, it's the input directory;
    we default to 'merged_output.obj' as the output file.
    If two arguments, the second is the output .obj filename.
    """
    if len(sys.argv) < 2:
        print("Usage: python merge_obj.py <input_directory> [output_file]")
        sys.exit(1)

    input_dir = sys.argv[1]
    if len(sys.argv) == 3:
        out_file = sys.argv[2]
    else:
        out_file = "merged_output.obj"

    merge_obj_files_in_memory(input_dir, out_file)
    print(f"Finished merging OBJ files in '{input_dir}' into '{out_file}'.")
