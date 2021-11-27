import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
from obj import *

pygame.init()
screen = pygame.display.set_mode((1200, 720), pygame.OPENGL | pygame.DOUBLEBUF)
glClearColor(0.1, 0.2, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
clock = pygame.time.Clock()

vertex_shader_1 = """
#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 ccolor;

uniform mat4 theMatrix;

out vec3 mycolor;

void main() 
{
  gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1);
  mycolor = ccolor;
}
"""
vertex_shader_2 = """
#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec3 texcoords;

uniform mat4 theMatrix;
uniform vec3 light;

out vec2 vertexTexcoords;
out float intensity;

void main() 
{
  intensity = dot(normal, normalize(light - position));
  gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1);
  vertexTexcoords = texcoords.xy;
}
"""

fragment_shader_1 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform int clock;
in vec3 mycolor;

void main()
{
  fragColor = vec4(mycolor.yzx, 1.0f);
}
"""
fragment_shader_2 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform int clock;
in vec3 mycolor;

void main()
{
  fragColor = vec4(mycolor.xyz, 1.0f);
}
"""

fragment_shader_3 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform int clock;
in vec3 mycolor;

void main()
{
  fragColor = vec4(mycolor.zxy, 1.0f);
  
}
"""

fragment_shader_4 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform int clock;
in vec3 mycolor;
in float intensity;

void main()
{
  fragColor = vec4(0.776, 0.619, 0.082, 1.0f)  * intensity;
  
}
"""

fragment_shader_5 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform int clock;
in vec2 vertexTexcoords;
in float intensity;

uniform sampler2D tex;

void main()
{ 
  fragColor = texture(tex, vertexTexcoords) * intensity;
}
"""


cvs_1 = compileShader(vertex_shader_1, GL_VERTEX_SHADER)
cvs_2 = compileShader(vertex_shader_2, GL_VERTEX_SHADER)

cfs_1 = compileShader(fragment_shader_1, GL_FRAGMENT_SHADER)
cfs_2 = compileShader(fragment_shader_2, GL_FRAGMENT_SHADER)
cfs_3 = compileShader(fragment_shader_3, GL_FRAGMENT_SHADER)
cfs_4 = compileShader(fragment_shader_4, GL_FRAGMENT_SHADER)
cfs_5 = compileShader(fragment_shader_5, GL_FRAGMENT_SHADER)

shader_1 = compileProgram(cvs_1, cfs_1)
shader_2 = compileProgram(cvs_1, cfs_2)
shader_3 = compileProgram(cvs_1, cfs_3)
shader_4 = compileProgram(cvs_1, cfs_4)
shader_5 = compileProgram(cvs_2, cfs_5)

mesh = Obj('./demon.obj')
vertex_data = numpy.hstack((
  numpy.array(mesh.vertices, dtype=numpy.float32),
  numpy.array(mesh.normals, dtype=numpy.float32),
  numpy.array(mesh.tvertices, dtype=numpy.float32),
)).flatten()

index_data = numpy.array([[vertex[0] - 1 for vertex in face] for face in mesh.vfaces], dtype=numpy.uint32).flatten()

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)
glVertexAttribPointer(
  0, # location
  3, # size
  GL_FLOAT, # tipo
  GL_FALSE, # normalizados
  4 * 9, # stride
  ctypes.c_void_p(0)
)
glEnableVertexAttribArray(0)

element_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

glVertexAttribPointer(
  1, # location
  3, # size
  GL_FLOAT, # tipo
  GL_FALSE, # normalizados
  4 * 9, # stride
  ctypes.c_void_p(4 * 3)
)
glEnableVertexAttribArray(1)

glVertexAttribPointer(
  2, # location
  3, # size
  GL_FLOAT, # tipo
  GL_FALSE, # normalizados
  4 * 9, # stride
  ctypes.c_void_p(4 * 6)
)
glEnableVertexAttribArray(2)

texture_surface = pygame.image.load('./textura.jpg')
texture_data = pygame.image.tostring(texture_surface, 'RGB', True)
texture_buffer = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_buffer)
glTexImage2D(
  GL_TEXTURE_2D, # GLenum target,
 	0, # GLint level,
 	GL_RGB, # GLint internalformat,
 	texture_surface.get_width(), # GLsizei width,
 	texture_surface.get_height(), # GLsizei height,
 	0, # GLint border,
 	GL_RGB, # GLenum format,
 	GL_UNSIGNED_BYTE, # GLenum type,
 	texture_data
)



def makeMatrix(a):
  i = glm.mat4(1)

  translate = glm.translate(i, glm.vec3(0, -30, -100))
  rotate = glm.rotate(i, glm.radians(a), glm.vec3(x, y, z))
  scale = glm.scale(i, glm.vec3(0.3, 0.3, 0.3))

  model = translate * rotate * scale
  view = glm.lookAt(glm.vec3(0, 0, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
  projection = glm.perspective(glm.radians(45), 1200/720, 0.1, 1000.0)

  theMatrix = projection * view * model

  glUniformMatrix4fv(
    glGetUniformLocation(shader, 'theMatrix'),
    1,
    GL_FALSE,
    glm.value_ptr(theMatrix)
  )

glViewport(0, 0, 1200, 720)

a = 0
x = 0
y = 0.5
z = 0
shader = shader_1

running = True
while running:
  glGenerateMipmap(GL_TEXTURE_2D)
  glUseProgram(shader)
  glUniform3f(
    glGetUniformLocation(shader, 'light'),
    0, 0, 10
  )
  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  makeMatrix(a)
  a += 1

  glUniform1i(
    glGetUniformLocation(shader, 'clock'),
    a
  )
  glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)
  pygame.display.flip()
  clock.tick(15)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_1:
         shader = shader_1
      elif event.key == pygame.K_2:
         shader = shader_2
      elif event.key == pygame.K_3:
         shader = shader_3
      elif event.key == pygame.K_4:
         shader = shader_4
      elif event.key == pygame.K_5:
         shader = shader_5
      elif event.key == pygame.K_q:
         x += 0.3
      elif event.key == pygame.K_w:
         x += -0.3 
      elif event.key == pygame.K_a:
         y += 0.3
      elif event.key == pygame.K_s:
         y += -0.3
      elif event.key == pygame.K_z:
         z += 0.3
      elif event.key == pygame.K_x:
         z += -0.3
